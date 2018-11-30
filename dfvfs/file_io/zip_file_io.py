# -*- coding: utf-8 -*-
"""The ZIP extracted file-like object implementation."""

from __future__ import unicode_literals

# Note: that zipfile.ZipExtFile is not seekable, hence it is wrapped in
# an instance of file_io.FileIO.

import os
import zipfile

from dfvfs.file_io import file_io
from dfvfs.resolver import resolver


class ZipFile(file_io.FileIO):
  """File-like object using zipfile."""

  # The size of the uncompressed data buffer.
  _UNCOMPRESSED_DATA_BUFFER_SIZE = 16 * 1024 * 1024

  def __init__(self, resolver_context):
    """Initializes a file-like object.

    Args:
      resolver_context (Context): resolver context.
    """
    super(ZipFile, self).__init__(resolver_context)
    self._compressed_data = b''
    self._current_offset = 0
    self._file_system = None
    self._realign_offset = True
    self._uncompressed_data = b''
    self._uncompressed_data_offset = 0
    self._uncompressed_data_size = 0
    self._uncompressed_stream_size = None
    self._zip_ext_file = None
    self._zip_file = None
    self._zip_info = None

  def _Close(self):
    """Closes the file-like object."""
    if self._zip_ext_file:
      self._zip_ext_file.close()
      self._zip_ext_file = None

    self._zip_file = None
    self._zip_info = None

    self._file_system.Close()
    self._file_system = None

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
    if not path_spec:
      raise ValueError('Missing path specification.')

    file_system = resolver.Resolver.OpenFileSystem(
        path_spec, resolver_context=self._resolver_context)

    file_entry = file_system.GetFileEntryByPathSpec(path_spec)
    if not file_entry:
      file_system.Close()
      raise IOError('Unable to retrieve file entry.')

    if not file_entry.IsFile():
      file_system.Close()
      raise IOError('Not a regular file.')

    self._file_system = file_system
    self._zip_file = self._file_system.GetZipFile()
    self._zip_info = file_entry.GetZipInfo()

    self._current_offset = 0
    self._uncompressed_stream_size = self._zip_info.file_size

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
      raise IOError(
          'Unable to open ZIP file with error: {0!s}'.format(exception))

    self._uncompressed_data = b''
    self._uncompressed_data_size = 0
    self._uncompressed_data_offset = 0

    while uncompressed_data_offset > 0:
      self._ReadCompressedData(self._UNCOMPRESSED_DATA_BUFFER_SIZE)

      if uncompressed_data_offset < self._uncompressed_data_size:
        self._uncompressed_data_offset = uncompressed_data_offset
        break

      uncompressed_data_offset -= self._uncompressed_data_size

  def _ReadCompressedData(self, read_size):
    """Reads compressed data from the file-like object.

    Args:
      read_size (int): number of bytes of compressed data to read.
    """
    self._uncompressed_data = self._zip_ext_file.read(read_size)
    self._uncompressed_data_size = len(self._uncompressed_data)

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
      raise IOError('Invalid current offset value less than zero.')

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

      self._ReadCompressedData(self._UNCOMPRESSED_DATA_BUFFER_SIZE)

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

    if offset != self._current_offset:
      self._current_offset = offset
      self._realign_offset = True

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
