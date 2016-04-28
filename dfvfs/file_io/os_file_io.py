# -*- coding: utf-8 -*-
"""The operating system file-like object implementation."""

import stat
import os

import pysmdev

from dfvfs import dependencies
from dfvfs.file_io import file_io
from dfvfs.lib import errors
from dfvfs.lib import py2to3


dependencies.CheckModuleVersion(u'pysmdev')


class OSFile(file_io.FileIO):
  """Class that implements a file-like object using os."""

  def __init__(self, resolver_context):
    """Initializes the file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
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
      path_spec: optional path specification (instance of PathSpec).
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec:
      raise ValueError(u'Missing path specification.')

    if path_spec.HasParent():
      raise errors.PathSpecError(u'Unsupported path specification with parent.')

    location = getattr(path_spec, u'location', None)

    if location is None:
      raise errors.PathSpecError(u'Path specification missing location.')

    # Windows does not support running os.stat on device files so we use
    # libsmdev to do an initial check.
    try:
      is_device = pysmdev.check_device(location)
    except IOError as exception:
      # Since os.stat() will not recognize Windows device file names and
      # will return '[Error 87] The parameter is incorrect' we check here
      # if pysmdev exception message contains ' access denied ' and raise
      # AccessError instead.

      # Note that exception.message no longer works in Python 3.
      exception_string = str(exception)
      if not isinstance(exception_string, py2to3.UNICODE_TYPE):
        exception_string = py2to3.UNICODE_TYPE(
            exception_string, errors=u'replace')

      if u' access denied ' in exception_string:
        raise errors.AccessError(
            u'Access denied to file: {0:s} with error: {1:s}'.format(
                location, exception_string))
      is_device = False

    if not is_device:
      try:
        stat_info = os.stat(location)
      except OSError as exception:
        raise IOError(u'Unable to open file with error: {0:s}.'.format(
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

    if size is None:
      size = self._size - self._file_object.tell()

    return self._file_object.read(size)

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks an offset within the file-like object.

    Args:
      offset: The offset to seek.
      whence: Optional value that indicates whether offset is an absolute
              or relative position within the file.

    Raises:
      IOError: if the seek failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    # For a yet unknown reason a Python file-like object on Windows allows for
    # invalid whence values to be passed to the seek function. This check
    # makes sure the behavior of the function is the same on all platforms.
    if whence not in [os.SEEK_SET, os.SEEK_CUR, os.SEEK_END]:
      raise IOError(u'Unsupported whence.')

    self._file_object.seek(offset, whence)

  def get_offset(self):
    """Returns the current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._file_object.tell()

  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._size
