# -*- coding: utf-8 -*-
"""The fake file-like object implementation."""

import os

from dfvfs.file_io import file_io
from dfvfs.lib import errors


class FakeFile(file_io.FileIO):
  """Fake file input/output (IO) object."""

  def __init__(self, resolver_context, path_spec, file_data):
    """Initializes a file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
      file_data (bytes): fake file data.
    """
    super(FakeFile, self).__init__(resolver_context, path_spec)
    self._current_offset = 0
    self._file_data = file_data
    self._size = 0

  def _Close(self):
    """Closes the file-like object."""
    return

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
    if self._path_spec.HasParent():
      raise errors.PathSpecError('Unsupported path specification with parent.')

    location = getattr(self._path_spec, 'location', None)
    if location is None:
      raise errors.PathSpecError('Path specification missing location.')

    self._current_offset = 0
    self._size = len(self._file_data)

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

    if self._current_offset < 0:
      raise IOError((
          f'Invalid current offset: {self._current_offset:d} value less than '
          f'zero.'))

    if self._file_data is None or self._current_offset >= self._size:
      return b''

    if size is None:
      size = self._size
    if self._current_offset + size > self._size:
      size = self._size - self._current_offset

    start_offset = self._current_offset
    self._current_offset += size
    return self._file_data[start_offset:self._current_offset]

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

    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self._size
    elif whence != os.SEEK_SET:
      raise IOError('Unsupported whence.')

    if offset < 0:
      raise IOError('Invalid offset value less than zero.')

    self._current_offset = offset

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

    return self._current_offset

  def get_size(self):
    """Retrieves the size of the file-like object.

    Returns:
      int: size of the file data.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    return self._size
