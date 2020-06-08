# -*- coding: utf-8 -*-
"""The operating system file-like object implementation."""

from __future__ import unicode_literals

import stat
import os

import pysmdev

from dfvfs.file_io import file_io
from dfvfs.lib import errors


class OSFile(file_io.FileIO):
  """File-like object using os."""

  def __init__(self, resolver_context):
    """Initializes a file-like object.

    Args:
      resolver_context (Context): resolver context.
    """
    super(OSFile, self).__init__(resolver_context)
    self._file_object = None
    self._size = 0

  def _Close(self):
    """Closes the file-like object."""
    self._file_object.close()
    self._file_object = None

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
      raise ValueError('Missing path specification.')

    if path_spec.HasParent():
      raise errors.PathSpecError('Unsupported path specification with parent.')

    location = getattr(path_spec, 'location', None)

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
            'Access denied to file: {0:s} with error: {1!s}'.format(
                location, exception))

      is_device = False

    if not is_device:
      try:
        stat_info = os.stat(location)
      except OSError as exception:
        raise IOError('Unable to open file with error: {0!s}.'.format(
            exception))

      # In case the libsmdev check is not able to detect the device also use
      # the stat information.
      if stat.S_ISCHR(stat_info.st_mode) or stat.S_ISBLK(stat_info.st_mode):
        is_device = True

    if is_device:
      self._file_object = pysmdev.handle()
      self._file_object.open(location, mode=mode)
      self._size = self._file_object.media_size

    else:
      self._file_object = open(location, mode=mode)
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
