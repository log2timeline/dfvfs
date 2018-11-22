# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) file-like object interface."""

from __future__ import unicode_literals

import abc
import os


class FileIO(object):
  """VFS file-like object interface."""

  # pylint: disable=redundant-returns-doc

  def __init__(self, resolver_context):
    """Initializes a file-like object.

    Args:
      resolver_context (Context): resolver context.
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
      OSError: if the close failed.
    """

  @abc.abstractmethod
  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec (Optional[PathSpec]): path specification.
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      OSError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.
  # pylint: disable=invalid-name

  def open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec (Optional[PathSpec]): path specification.
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object was already opened or the open failed.
      OSError: if the file-like object was already opened or the open failed.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification or mode is invalid.
    """
    if self._is_open and not self._is_cached:
      raise IOError('Already open.')

    if mode != 'rb':
      raise ValueError('Unsupported mode: {0:s}.'.format(mode))

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
      OSError: if the file-like object was not opened or the close failed.
    """
    if not self._is_open:
      raise IOError('Not opened.')

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
      size (Optional[int]): number of bytes to read, where None is all
          remaining data.

    Returns:
      bytes: data read.

    Raises:
      IOError: if the read failed.
      OSError: if the read failed.
    """

  @abc.abstractmethod
  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks to an offset within the file-like object.

    Args:
      offset (int): offset to seek.
      whence (Optional[int]): value that indicates whether offset is an
          absolute or relative position within the file.

    Raises:
      IOError: if the seek failed.
      OSError: if the seek failed.
    """

  # get_offset() is preferred above tell() by the libbfio layer used in libyal.
  @abc.abstractmethod
  def get_offset(self):
    """Retrieves the current offset into the file-like object.

    Returns:
      int: current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """

  # Pythonesque alias for get_offset().
  def tell(self):
    """Retrieves the current offset into the file-like object."""
    return self.get_offset()

  @abc.abstractmethod
  def get_size(self):
    """Retrieves the size of the file-like object.

    Returns:
      int: size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """

  def seekable(self):
    """Determines if a file-like object is seekable.

    Returns:
      bool: True since a file IO object provides a seek method.
    """
    return True
