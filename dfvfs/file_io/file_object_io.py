# -*- coding: utf-8 -*-
"""The file object file-like object implementation."""

import abc
import os

from dfvfs.file_io import file_io


class FileObjectIO(file_io.FileIO):
  """Base class for file object-based file-like object."""

  def __init__(self, resolver_context, file_object=None):
    """Initializes the file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      file_object: optional file-like object.
    """
    super(FileObjectIO, self).__init__(resolver_context)
    self._file_object = file_object
    self._size = None

    if file_object:
      self._file_object_set_in_init = True
    else:
      self._file_object_set_in_init = False

  def _Close(self):
    """Closes the file-like object.

    If the file-like object was passed in the init function the file
    object-based file-like object does not control the file-like object
    and should not actually close it.
    """
    if not self._file_object_set_in_init:
      self._file_object.close()
      self._file_object = None

  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: optional the path specification (instance of PathSpec).
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not self._file_object_set_in_init and not path_spec:
      raise ValueError(u'Missing path specification.')

    if self._file_object_set_in_init:
      return

    self._file_object = self._OpenFileObject(path_spec)
    if not self._file_object:
      raise IOError(u'Unable to open missing file-like object.')

  @abc.abstractmethod
  def _OpenFileObject(self, path_spec):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).

    Returns:
      A file-like object.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.

  def read(self, size=None):
    """Reads a byte string from the file-like object at the current offset.

    The function will read a byte string of the specified size or
    all of the remaining data if no size was specified.

    Args:
      size: optional integer value containing the number of bytes to read.
            Default is all remaining data (None).

    Returns:
      A byte string containing the data read.

    Raises:
      IOError: if the read failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._file_object.read(size=size)

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks an offset within the file-like object.

    Args:
      offset: the offset to seek.
      whence: optional value that indicates whether offset is an absolute
              or relative position within the file.

    Raises:
      IOError: if the seek failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    self._file_object.seek(offset, whence)

  def get_offset(self):
    """Returns the current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if not hasattr(self._file_object, u'get_offset'):
      return self._file_object.tell()
    return self._file_object.get_offset()

  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if not hasattr(self._file_object, u'get_size'):
      if not self._size:
        current_offset = self.get_offset()
        self.seek(0, os.SEEK_END)
        self._size = self.get_offset()
        self.seek(current_offset, os.SEEK_SET)
      return self._size

    return self._file_object.get_size()
