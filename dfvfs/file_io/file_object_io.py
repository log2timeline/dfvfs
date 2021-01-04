# -*- coding: utf-8 -*-
"""The file object file input/output (IO) object implementation."""

import abc
import os

from dfvfs.file_io import file_io


class FileObjectIO(file_io.FileIO):
  """Base class for file object-based file input/output (IO) object."""

  # pylint: disable=redundant-returns-doc

  def __init__(self, resolver_context, path_spec):
    """Initializes a file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(FileObjectIO, self).__init__(resolver_context, path_spec)
    self._file_object = None
    self._size = None

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
      OSError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
    """
    self._file_object = self._OpenFileObject(self._path_spec)
    if not self._file_object:
      raise IOError('Unable to open missing file-like object.')

  # pylint: disable=redundant-returns-doc
  @abc.abstractmethod
  def _OpenFileObject(self, path_spec):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      FileIO: a file-like object.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """

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

    # Do not pass the size argument as a keyword argument since it breaks
    # some file-like object implementations.
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

    if not hasattr(self._file_object, 'get_offset'):
      return self._file_object.tell()
    return self._file_object.get_offset()

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

    if not hasattr(self._file_object, 'get_size'):
      if not self._size:
        current_offset = self.get_offset()
        self.seek(0, os.SEEK_END)
        self._size = self.get_offset()
        self.seek(current_offset, os.SEEK_SET)
      return self._size

    return self._file_object.get_size()
