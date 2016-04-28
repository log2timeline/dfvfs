# -*- coding: utf-8 -*-
"""The zip extracted file-like object implementation."""

# Note: that zipfile.ZipExtFile is not seekable, hence it is wrapped in
# an instance of file_io.FileIO.

import os

from dfvfs.file_io import file_io
from dfvfs.resolver import resolver


class ZipFile(file_io.FileIO):
  """Class that implements a file-like object using zipfile."""

  # The size of the uncompressed data buffer.
  _UNCOMPRESSED_DATA_BUFFER_SIZE = 16 * 1024 * 1024

  def __init__(self, resolver_context):
    """Initializes the file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
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
      path_spec: optional the path specification (instance of PathSpec).
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec:
      raise ValueError(u'Missing path specification.')

    file_system = resolver.Resolver.OpenFileSystem(
        path_spec, resolver_context=self._resolver_context)

    file_entry = file_system.GetFileEntryByPathSpec(path_spec)
    if not file_entry:
      file_system.Close()
      raise IOError(u'Unable to retrieve file entry.')

    self._file_system = file_system
    self._zip_file = self._file_system.GetZipFile()
    self._zip_info = file_entry.GetZipInfo()

    self._current_offset = 0
    self._uncompressed_stream_size = self._zip_info.file_size

  def _AlignUncompressedDataOffset(self, uncompressed_data_offset):
    """Aligns the compressed file with the uncompressed data offset.

    Args:
      uncompressed_data_offset: the uncompressed data offset.
    """
    if self._zip_ext_file:
      self._zip_ext_file.close()
      self._zip_ext_file = None

    self._zip_ext_file = self._zip_file.open(self._zip_info, 'r')

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
      read_size: the number of bytes of compressed data to read.
    """
    self._uncompressed_data = self._zip_ext_file.read(read_size)
    self._uncompressed_data_size = len(self._uncompressed_data)

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

    if self._current_offset < 0:
      raise IOError(u'Invalid current offset value less than zero.')

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

    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self._uncompressed_stream_size
    elif whence != os.SEEK_SET:
      raise IOError(u'Unsupported whence.')

    if offset < 0:
      raise IOError(u'Invalid offset value less than zero.')

    if offset != self._current_offset:
      self._current_offset = offset
      self._realign_offset = True

  def get_offset(self):
    """Returns the current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._current_offset

  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._uncompressed_stream_size
