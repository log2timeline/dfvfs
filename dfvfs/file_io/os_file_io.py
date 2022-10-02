# -*- coding: utf-8 -*-
"""The operating system file-like object implementation."""

import stat
import os

import pysmdev

from dfvfs.file_io import file_io
from dfvfs.lib import definitions
from dfvfs.lib import errors


class OSFile(file_io.FileIO):
  """File input/output (IO) object that uses the operating system."""

  def __init__(self, resolver_context, path_spec):
    """Initializes a file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(OSFile, self).__init__(resolver_context, path_spec)
    self._file_object = None
    self._size = 0

  def _Close(self):
    """Closes the file-like object."""
    self._file_object.close()
    self._file_object = None

  def _Open(self, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      MountPointError: if the mount point specified in the path specification
          does not exist.
      OSError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
    """
    location = getattr(self._path_spec, 'location', None)

    if self._path_spec.HasParent():
      parent_path_spec = self._path_spec.parent
      if parent_path_spec.type_indicator != definitions.TYPE_INDICATOR_MOUNT:
        raise errors.PathSpecError(
            'Unsupported path specification with parent.')

      mount_path_spec = self._resolver_context.GetMountPoint(
          parent_path_spec.identifier)
      if not mount_path_spec:
        raise errors.MountPointError(
            f'No such mount point: {parent_path_spec.identifier:s}')

      if (mount_path_spec.type_indicator != definitions.TYPE_INDICATOR_OS or
          mount_path_spec.parent):
        raise errors.MountPointError(
            'Unsupported mount point path specification.')

      mount_path = mount_path_spec.location
      if mount_path[-1] == os.path.sep:
        mount_path = mount_path[:-1]

      # Cannot use os.path.join() here since location is prefixed with a path
      # segment separator.
      location = ''.join([mount_path, location])

    if location is None:
      raise errors.PathSpecError('Path specification missing location.')

    # Windows does not support running os.stat on device files so we use
    # libsmdev to do an initial check.
    try:
      is_device = pysmdev.check_device(location)
    except IOError as exception:
      # Since os.stat() will not recognize Windows device file names and
      # will return '[Error 87] The parameter is incorrect' we check here
      # if pysmdev exception message contains ' access denied ' and raise
      # AccessError instead.
      if ' access denied ' in str(exception):
        raise errors.AccessError(
            f'Access denied to file: {location:s} with error: {exception!s}')

      is_device = False

    if not is_device:
      try:
        stat_info = os.stat(location)
      except OSError as exception:
        raise IOError(f'Unable to open file with error: {exception!s}')

      # In case the libsmdev check is not able to detect the device also use
      # the stat information.
      if stat.S_ISCHR(stat_info.st_mode) or stat.S_ISBLK(stat_info.st_mode):
        is_device = True

    if is_device:
      smdev_handle = pysmdev.handle()
      smdev_handle.open(location, mode=mode)

      self._file_object = smdev_handle
      self._size = smdev_handle.media_size

    else:
      self._file_object = open(location, mode=mode)  # pylint: disable=consider-using-with,unspecified-encoding
      self._size = stat_info.st_size

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

    if size is None:
      size = self._size - self._file_object.tell()

    return self._file_object.read(size)

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

    # For a yet unknown reason a Python file-like object on Windows allows for
    # invalid whence values to be passed to the seek function. This check
    # makes sure the behavior of the function is the same on all platforms.
    if whence not in (os.SEEK_CUR, os.SEEK_END, os.SEEK_SET):
      raise IOError('Unsupported whence.')

    self._file_object.seek(offset, whence)

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

    return self._file_object.tell()

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

    return self._size
