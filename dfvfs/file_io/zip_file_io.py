# -*- coding: utf-8 -*-
"""The ZIP extracted file-like object implementation."""

import io
import os
import zipfile

from dfvfs.file_io import file_io
from dfvfs.resolver import resolver


class ZipFile(file_io.FileIO):
  """File input/output (IO) object using zipfile."""

  # The size of the uncompressed data buffer.
  _UNCOMPRESSED_DATA_BUFFER_SIZE = 64 * 1024

  def __init__(self, resolver_context, path_spec):
    """Initializes a file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(ZipFile, self).__init__(resolver_context, path_spec)
    self._compressed_data = b''
    self._current_offset = 0
    self._file_system = None
    self._is_seekable = False
    self._realign_offset = True
    self._uncompressed_data = b''
    self._uncompressed_data_offset = 0
    self._uncompressed_data_size = 0
    self._uncompressed_stream_size = None
    self._zip_ext_file = None
    self._zip_file = None
    self._zip_info = None

  def _AlignUncompressedDataOffset(self, uncompressed_data_offset):
    """Aligns the compressed file with the uncompressed data offset.

    Args:
      uncompressed_data_offset (int): uncompressed data offset.

    Raises:
      IOError: if the ZIP file could not be opened.
      OSError: if the ZIP file could not be opened.
    """
    if self._zip_ext_file:
      self._zip_ext_file.close()
      self._zip_ext_file = None

    try:
      # The open can fail if the file path in the local file header
      # does not use the same path segment separator as the corresponding
      # entry in the central directory.
      self._zip_ext_file = self._zip_file.open(self._zip_info, 'r')
    except zipfile.BadZipfile as exception:
      raise IOError(f'Unable to open ZIP file with error: {exception!s}')

    self._uncompressed_data = b''
    self._uncompressed_data_size = 0
    self._uncompressed_data_offset = 0

    while uncompressed_data_offset > 0:
      self._uncompressed_data = self._zip_ext_file.read(
          self._UNCOMPRESSED_DATA_BUFFER_SIZE)
      self._uncompressed_data_size = len(self._uncompressed_data)

      if uncompressed_data_offset < self._uncompressed_data_size:
        self._uncompressed_data_offset = uncompressed_data_offset
        break

      uncompressed_data_offset -= self._uncompressed_data_size

  def _Close(self):
    """Closes the file-like object."""
    if self._zip_ext_file:
      self._zip_ext_file.close()
      self._zip_ext_file = None

    self._zip_file = None
    self._zip_info = None

    self._file_system = None

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
    file_system = resolver.Resolver.OpenFileSystem(
        self._path_spec, resolver_context=self._resolver_context)

    file_entry = file_system.GetFileEntryByPathSpec(self._path_spec)
    if not file_entry:
      raise IOError('Unable to retrieve file entry.')

    if not file_entry.IsFile():
      raise IOError('Not a regular file.')

    zip_file = file_system.GetZipFile()
    zip_info = file_entry.GetZipInfo()

    try:
      # The open can fail if the file path in the local file header
      # does not use the same path segment separator as the corresponding
      # entry in the central directory.
      zip_ext_file = zip_file.open(zip_info, 'r')
    except zipfile.BadZipfile as exception:
      raise IOError(f'Unable to open ZIP file with error: {exception!s}')

    self._file_system = file_system
    self._zip_file = zip_file
    self._zip_info = zip_info
    self._zip_ext_file = zip_ext_file

    self._uncompressed_stream_size = self._zip_info.file_size

    try:
      # ZipExtFile in Python 3.6 does not support seek().
      self._zip_ext_file.seek(0, os.SEEK_SET)
      self._is_seekable = True
    except io.UnsupportedOperation:
      self._is_seekable = False

  def _ReadNonSeekableZipExtFile(self, size):
    """Reads a byte string from a non-seekable file-like object.

    The function will read a byte string of the specified size or
    all of the remaining data if no size was specified.

    Args:
      size (int): number of bytes to read, where None is all
          remaining data.

    Returns:
      bytes: data read.

    Raises:
      IOError: if the read failed.
      OSError: if the read failed.
    """
    if self._current_offset > self._uncompressed_stream_size:
      return b''

    if (size is None or
        self._current_offset + size > self._uncompressed_stream_size):
      size = self._uncompressed_stream_size - self._current_offset

    if self._realign_offset:
      self._AlignUncompressedDataOffset(self._current_offset)
      self._realign_offset = False

    uncompressed_data = b''

    # Read in full blocks of uncompressed data.
    while self._uncompressed_data_offset + size > self._uncompressed_data_size:
      uncompressed_data = b''.join([
          uncompressed_data,
          self._uncompressed_data[self._uncompressed_data_offset:]])

      remaining_uncompressed_data_size = (
          self._uncompressed_data_size - self._uncompressed_data_offset)

      self._current_offset += remaining_uncompressed_data_size
      size -= remaining_uncompressed_data_size

      self._uncompressed_data = self._zip_ext_file.read(
          self._UNCOMPRESSED_DATA_BUFFER_SIZE)
      self._uncompressed_data_size = len(self._uncompressed_data)
      self._uncompressed_data_offset = 0

    # Read in partial block of uncompressed data.
    if (size > 0 and
        self._uncompressed_data_offset + size <= self._uncompressed_data_size):
      slice_start_offset = self._uncompressed_data_offset
      slice_end_offset = slice_start_offset + size

      uncompressed_data = b''.join([
          uncompressed_data,
          self._uncompressed_data[slice_start_offset:slice_end_offset]])

      self._uncompressed_data_offset += size
      self._current_offset += size

    return uncompressed_data

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

    if self._is_seekable:
      uncompressed_data = self._zip_ext_file.read(size)

      self._current_offset += len(uncompressed_data)
    else:
      uncompressed_data = self._ReadNonSeekableZipExtFile(size)

    return uncompressed_data

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
      offset += self._uncompressed_stream_size
    elif whence != os.SEEK_SET:
      raise IOError('Unsupported whence.')

    if offset < 0:
      raise IOError('Invalid offset value less than zero.')

    if self._is_seekable:
      self._zip_ext_file.seek(offset, os.SEEK_SET)
    elif offset != self._current_offset:
      self._realign_offset = True

    # ZipExtFile tell() is not POSIX compliant hence the current offset
    # is tracked seperately.
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
      int: size of the file-like object data.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    return self._uncompressed_stream_size
