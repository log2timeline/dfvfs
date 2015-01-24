# -*- coding: utf-8 -*-
"""The Volume Shadow Snapshots (VSS) file-like object implementation."""

import os

from dfvfs.file_io import file_io
from dfvfs.lib import errors
from dfvfs.lib import vshadow
from dfvfs.resolver import resolver


class VShadowFile(file_io.FileIO):
  """Class that implements a file-like object using pyvshadow."""

  def __init__(self, resolver_context, vshadow_volume=None, vshadow_store=None):
    """Initializes the file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      vshadow_volume: optional VSS volume object (instance of
                      pyvshadow.volume). The default is None.
      vshadow_store: optional VSS store object (instance of pyvshadow.store).
                     The default is None.

    Raises:
      ValueError: if vshadow_store provided but vshadow_volume is not.
    """
    if vshadow_store is not None and vshadow_volume is None:
      raise ValueError(
          u'VShadow store object provided without corresponding volume object.')

    super(VShadowFile, self).__init__(resolver_context)
    self._vshadow_volume = vshadow_volume
    self._vshadow_store = vshadow_store

    if vshadow_store:
      self._vshadow_store_set_in_init = True
    else:
      self._vshadow_store_set_in_init = False
    self._is_open = False

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.

  def open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: optional path specification (instance of path.PathSpec).
                 The default is None.
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      IOError: if the open file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification or mode is invalid.
    """
    if not self._vshadow_store_set_in_init and not path_spec:
      raise ValueError(u'Missing path specfication.')

    if mode != 'rb':
      raise ValueError(u'Unsupport mode: {0:s}.'.format(mode))

    if self._is_open:
      raise IOError(u'Already open.')

    if not self._vshadow_store_set_in_init:
      store_index = vshadow.VShadowPathSpecGetStoreIndex(path_spec)
      if store_index is None:
        raise errors.PathSpecError(
            u'Unable to retrieve store index from path specification.')

      file_system = resolver.Resolver.OpenFileSystem(
          path_spec, resolver_context=self._resolver_context)
      self._vshadow_volume = file_system.GetVShadowVolume()

      if (store_index < 0 or
          store_index >= self._vshadow_volume.number_of_stores):
        raise errors.PathSpecError((
            u'Unable to retrieve VSS store: {0:d} from path '
            u'specification.').format(store_index))

      self._vshadow_store = self._vshadow_volume.get_store(store_index)

    self._is_open = True

  def close(self):
    """Closes the file-like object.

    Raises:
      IOError: if the close failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    self._resolver_context.RemoveFileObject(self)

    if not self._vshadow_store_set_in_init:
      self._vshadow_store = None

    self._is_open = False

  def read(self, size=None):
    """Reads a byte string from the file-like object at the current offset.

       The function will read a byte string of the specified size or
       all of the remaining data if no size was specified.

    Args:
      size: Optional integer value containing the number of bytes to read.
            Default is all remaining data (None).

    Returns:
      A byte string containing the data read.

    Raises:
      IOError: if the read failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._vshadow_store.read(size)

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks an offset within the file-like object.

    Args:
      offset: The offset to seek.
      whence: Optional value that indicates whether offset is an absolute
              or relative position within the file. Default is SEEK_SET.

    Raises:
      IOError: if the seek failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    self._vshadow_store.seek(offset, whence)

  def get_offset(self):
    """Returns the current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._vshadow_store.get_offset()

  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._vshadow_store.volume_size
