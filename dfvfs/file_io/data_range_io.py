# -*- coding: utf-8 -*-
"""The data range file-like object."""

import os

from dfvfs.file_io import file_io
from dfvfs.lib import errors
from dfvfs.resolver import resolver


class DataRange(file_io.FileIO):
  """File input/output (IO) object that maps an in-file data range.

  The data range object allows to expose a single partition within
  a full disk image as a separate file-like object by mapping
  the data range (offset and size) of the volume on top of the full disk
  image.
  """

  def __init__(self, resolver_context, path_spec):
    """Initializes a file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(DataRange, self).__init__(resolver_context, path_spec)
    self._current_offset = 0
    self._file_object = None
    self._range_offset = -1
    self._range_size = -1

  def _Close(self):
    """Closes the file-like object.

    If the file-like object was passed in the init function
    the data range file-like object does not control the file-like object
    and should not actually close it.
    """
    self._file_object = None
    self._range_offset = -1
    self._range_size = -1

  def _Open(self, mode='rb'):
    """Opens the file-like object.

    Args:
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      OSError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
    """
    if not self._path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    range_offset = getattr(self._path_spec, 'range_offset', None)
    range_size = getattr(self._path_spec, 'range_size', None)

    if range_offset is None or range_size is None:
      raise errors.PathSpecError(
          'Path specification missing range offset and range size.')

    self._SetRange(range_offset, range_size)
    self._file_object = resolver.Resolver.OpenFileObject(
        self._path_spec.parent, resolver_context=self._resolver_context)

  def _SetRange(self, range_offset, range_size):
    """Sets the data range (offset and size).

    The data range is used to map a range of data within one file
    (e.g. a single partition within a full disk image) as a file-like object.

    Args:
      range_offset (int): start offset of the data range.
      range_size (int): size of the data range.

    Raises:
      ValueError: if the range offset or range size is invalid.
    """
    if range_offset < 0:
      raise ValueError(
          f'Invalid range offset: {range_offset:d} value out of bounds.')

    if range_size < 0:
      raise ValueError(
          f'Invalid range size: {range_size:d} value out of bounds.')

    self._range_offset = range_offset
    self._range_size = range_size
    self._current_offset = 0

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

    if self._range_offset < 0 or self._range_size < 0:
      raise IOError('Invalid data range.')

    if self._current_offset < 0:
      raise IOError((
          f'Invalid current offset: {self._current_offset:d} value less than '
          f'zero.'))

    if self._current_offset >= self._range_size:
      return b''

    if size is None:
      size = self._range_size
    if self._current_offset + size > self._range_size:
      size = self._range_size - self._current_offset

    self._file_object.seek(
        self._range_offset + self._current_offset, os.SEEK_SET)

    data = self._file_object.read(size)

    self._current_offset += len(data)

    return data

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

    if self._current_offset < 0:
      raise IOError((
          f'Invalid current offset: {self._current_offset:d} value less than '
          f'zero.'))

    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self._range_size
    elif whence != os.SEEK_SET:
      raise IOError('Unsupported whence.')
    if offset < 0:
      raise IOError('Invalid offset value less than zero.')
    self._current_offset = offset

  def get_offset(self):
    """Retrieves the current offset into the file-like object.

    Returns:
      int: current offset in the data range.

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
      int: size of the data range.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    return self._range_size
