# -*- coding: utf-8 -*-
"""The Volume Shadow Snapshots (VSS) file-like object implementation."""

import os

from dfvfs.file_io import file_io
from dfvfs.lib import errors
from dfvfs.lib import vshadow_helper
from dfvfs.resolver import resolver


class VShadowFile(file_io.FileIO):
  """File input/output (IO) object using pyvshadow."""

  def __init__(self, resolver_context, path_spec):
    """Initializes a file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(VShadowFile, self).__init__(resolver_context, path_spec)
    self._file_system = None
    self._vshadow_store = None

  def _Close(self):
    """Closes the file-like object."""
    self._vshadow_store = None

    self._file_system = None

  def _Open(self, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      OSError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
    """
    store_index = vshadow_helper.VShadowPathSpecGetStoreIndex(self._path_spec)
    if store_index is None:
      raise errors.PathSpecError(
          'Unable to retrieve store index from path specification.')

    self._file_system = resolver.Resolver.OpenFileSystem(
        self._path_spec, resolver_context=self._resolver_context)
    vshadow_volume = self._file_system.GetVShadowVolume()

    if (store_index < 0 or
        store_index >= vshadow_volume.number_of_stores):
      raise errors.PathSpecError((
          f'Unable to retrieve VSS store: {store_index:d} from path '
          f'specification.'))

    vshadow_store = vshadow_volume.get_store(store_index)
    if not vshadow_store.has_in_volume_data():
      raise IOError((
          f'Unable to open VSS store: {store_index:d} without in-volume '
          f'stored data.'))

    self._vshadow_store = vshadow_store

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.
  # pylint: disable=invalid-name

  def read(self, size=None):
    """Reads a byte string from the file-like object at the current offset.

    The function will read a byte string of the specified size or
    all of the remaining data if no size was specified.

    Args:
      size (Optional[int]): number of bytes to read, where None is all
          remaining data.

    Returns:
      bytes: data read.

    Raises:
      IOError: if the read failed.
      OSError: if the read failed.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    return self._vshadow_store.read(size)

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks to an offset within the file-like object.

    Args:
      offset (int): offset to seek to.
      whence (Optional(int)): value that indicates whether offset is an absolute
          or relative position within the file.

    Raises:
      IOError: if the seek failed.
      OSError: if the seek failed.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    self._vshadow_store.seek(offset, whence)

  def get_offset(self):
    """Retrieves the current offset into the file-like object.

    Returns:
      int: current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    return self._vshadow_store.get_offset()

  def get_size(self):
    """Retrieves the size of the file-like object.

    Returns:
      int: size of the file-like object data.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    return self._vshadow_store.volume_size
