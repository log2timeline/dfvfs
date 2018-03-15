# -*- coding: utf-8 -*-
"""The file object file-like object implementation."""

from __future__ import unicode_literals

import abc
import os

from dfvfs.file_io import file_io


class FileObjectIO(file_io.FileIO):
  """Base class for file object-based file-like object."""

  def __init__(self, resolver_context, file_object=None):
    """Initializes a file-like object.

    Args:
      resolver_context (Context): resolver context.
      file_object (Optional[FileIO]): file-like object.
    """
    super(FileObjectIO, self).__init__(resolver_context)
    self._file_object = file_object
    self._file_object_set_in_init = bool(file_object)
    self._size = None

  def _Close(self):
    """Closes the file-like object.

    If the file-like object was passed in the init function the file
    object-based file-like object does not control the file-like object
    and should not actually close it.
    """
    if not self._file_object_set_in_init:
      try:
        # TODO: fix close being called for the same object multiple times.
        self._file_object.close()
      except IOError:
        pass
      self._file_object = None

  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec (Optional[PathSpec]): path specification.
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not self._file_object_set_in_init and not path_spec:
      raise ValueError('Missing path specification.')

    if self._file_object_set_in_init:
      return

    self._file_object = self._OpenFileObject(path_spec)
    if not self._file_object:
      raise IOError('Unable to open missing file-like object.')

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
    """
    if not self._is_open:
      raise IOError('Not opened.')

    self._file_object.seek(offset, whence)

  def get_offset(self):
    """Retrieves the current offset into the file-like object.

    Return:
      int: current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
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
