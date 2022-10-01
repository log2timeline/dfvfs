# -*- coding: utf-8 -*-
"""The Logical Volume Manager (LVM) file-like object implementation."""

import os

from dfvfs.file_io import file_io
from dfvfs.lib import errors
from dfvfs.lib import lvm_helper
from dfvfs.resolver import resolver


class LVMFile(file_io.FileIO):
  """File input/output (IO) object using pyvslvm."""

  def __init__(self, resolver_context, path_spec):
    """Initializes a file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(LVMFile, self).__init__(resolver_context, path_spec)
    self._file_system = None
    self._vslvm_logical_volume = None

  def _Close(self):
    """Closes the file-like object."""
    self._vslvm_logical_volume = None

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
    volume_index = lvm_helper.LVMPathSpecGetVolumeIndex(self._path_spec)
    if volume_index is None:
      raise errors.PathSpecError(
          'Unable to retrieve volume index from path specification.')

    self._file_system = resolver.Resolver.OpenFileSystem(
        self._path_spec, resolver_context=self._resolver_context)
    vslvm_volume_group = self._file_system.GetLVMVolumeGroup()

    if (volume_index < 0 or
        volume_index >= vslvm_volume_group.number_of_logical_volumes):
      raise errors.PathSpecError((
          f'Unable to retrieve logical volume index: {volume_index:d} from '
          f'path specification.'))

    self._vslvm_logical_volume = vslvm_volume_group.get_logical_volume(
        volume_index)

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

    return self._vslvm_logical_volume.read(size)

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

    self._vslvm_logical_volume.seek(offset, whence)

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

    return self._vslvm_logical_volume.get_offset()

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

    return self._vslvm_logical_volume.size
