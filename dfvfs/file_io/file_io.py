# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) file-like object interface."""

import abc
import os


# Since this class implements the file-like object interface
# the names of the interface functions are in lower case as an exception
# to the normal naming convention.


class FileIO(object):
  """Class that implements the VFS file-like object interface."""

  def __init__(self, resolver_context):
    """Initializes the file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
    """
    super(FileIO, self).__init__()
    self._is_cached = False
    self._is_open = False
    self._resolver_context = resolver_context

  @abc.abstractmethod
  def _Close(self):
    """Closes the file-like object.

    Raises:
      IOError: if the close failed.
    """

  @abc.abstractmethod
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

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.

  def open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: optional path specification (instance of PathSpec).
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object was already opened or the open failed.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification or mode is invalid.
    """
    if self._is_open and not self._is_cached:
      raise IOError(u'Already open.')

    if mode != 'rb':
      raise ValueError(u'Unsupport mode: {0:s}.'.format(mode))

    if not self._is_open:
      self._Open(path_spec=path_spec, mode=mode)
      self._is_open = True

      if path_spec and not self._resolver_context.GetFileObject(path_spec):
        self._resolver_context.CacheFileObject(path_spec, self)
        self._is_cached = True

    if self._is_cached:
      self._resolver_context.GrabFileObject(path_spec)

  def close(self):
    """Closes the file-like object.

    Raises:
      IOError: if the file-like object was not opened or the close failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if not self._is_cached:
      close_file_object = True
    elif self._resolver_context.ReleaseFileObject(self):
      self._is_cached = False
      close_file_object = True
    else:
      close_file_object = False

    if close_file_object:
      self._Close()
      self._is_open = False

  @abc.abstractmethod
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

  @abc.abstractmethod
  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks an offset within the file-like object.

    Args:
      offset: The offset to seek.
      whence: Optional value that indicates whether offset is an absolute
              or relative position within the file.

    Raises:
      IOError: if the seek failed.
    """

  # get_offset() is preferred above tell() by the libbfio layer used in libyal.
  @abc.abstractmethod
  def get_offset(self):
    """Returns the current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """

  # Pythonesque alias for get_offset().
  def tell(self):
    """Returns the current offset into the file-like object."""
    return self.get_offset()

  @abc.abstractmethod
  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """

  def seekable(self):
    """Determines if a file-like object is seekable.

    Returns:
      True, since a file IO object will provide seek.
    """
    return True
