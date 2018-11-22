# -*- coding: utf-8 -*-
"""The Logical Volume Manager (LVM) file-like object implementation."""

from __future__ import unicode_literals

import os

from dfvfs.file_io import file_io
from dfvfs.lib import errors
from dfvfs.lib import lvm
from dfvfs.resolver import resolver


class LVMFile(file_io.FileIO):
  """File-like object using pyvslvm."""

  def __init__(self, resolver_context):
    """Initializes a file-like object.

    Args:
      resolver_context (Context): resolver context.
    """
    super(LVMFile, self).__init__(resolver_context)
    self._file_system = None
    self._vslvm_logical_volume = None

  def _Close(self):
    """Closes the file-like object."""
    self._vslvm_logical_volume = None

    self._file_system.Close()
    self._file_system = None

  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec (PathSpec): path specification.
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      OSError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec:
      raise ValueError('Missing path specfication.')

    volume_index = lvm.LVMPathSpecGetVolumeIndex(path_spec)
    if volume_index is None:
      raise errors.PathSpecError(
          'Unable to retrieve volume index from path specification.')

    self._file_system = resolver.Resolver.OpenFileSystem(
        path_spec, resolver_context=self._resolver_context)
    vslvm_volume_group = self._file_system.GetLVMVolumeGroup()

    if (volume_index < 0 or
        volume_index >= vslvm_volume_group.number_of_logical_volumes):
      raise errors.PathSpecError((
          'Unable to retrieve LVM logical volume index: {0:d} from path '
          'specification.').format(volume_index))

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
