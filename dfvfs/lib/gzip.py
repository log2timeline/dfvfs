# -*- coding: utf-8 -*-
"""Gzip compressed stream file."""

from __future__ import unicode_literals

import os

from dtfabric.runtime import fabric as dtfabric_fabric

from dfvfs.compression import zlib_decompressor
from dfvfs.lib import data_format
from dfvfs.lib import errors


class _GzipDecompressorState(object):
  """Deflate decompressor wrapper for reading a gzip member.

  This class encapsulates the state of a deflate decompression object, as well
  as the location of the decompressor's source data.

  Attributes:
    last_read (int): offset into the gzip file of the next data to be fed to the
        decompression object.
    uncompressed_offset (int): offset into the uncompressed data in a gzip
        member last emitted by the state object.
  """

  _MAXIMUM_READ_SIZE = 1024 * 1024

  def __init__(self, stream_start):
    """Initializes a gzip member decompressor wrapper.

    Args:
      stream_start (int): offset to the compressed stream within the containing
          file object.
    """
    self._decompressor = zlib_decompressor.DeflateDecompressor()
    self.last_read = stream_start
    self.uncompressed_offset = 0
    self._compressed_data = b''

  def Read(self, file_object):
    """Reads the next uncompressed data from the gzip stream.

    Args:
      file_object (FileIO): file object that contains the compressed stream.

    Returns:
      bytes: next uncompressed data from the compressed stream.
    """
    file_object.seek(self.last_read, os.SEEK_SET)
    read_data = file_object.read(self._MAXIMUM_READ_SIZE)
    self.last_read = file_object.get_offset()
    compressed_data = b''.join([self._compressed_data, read_data])
    decompressed, extra_compressed = self._decompressor.Decompress(
        compressed_data)
    self._compressed_data = extra_compressed
    self.uncompressed_offset += len(decompressed)
    return decompressed

  def GetUnusedData(self):
    """Retrieves any bytes past the end of the compressed data.

    See https://docs.python.org/2/library/zlib.html#zlib.Decompress.unused_data

    Unused data can be any bytes after a Deflate compressed block (or chunk).

    Returns:
      bytes: data past the end of the compressed data, if any has been read from
          the gzip file.
    """
    return self._decompressor.unused_data


class GzipMember(data_format.DataFormat):
  """Gzip member.

  Gzip files have no index of members, so each member must be read
  sequentially before metadata and random seeks are possible. This class
  provides caching of gzip member data during the initial read of each member.

  Attributes:
    comment (str): comment stored in the member.
    member_end_offset (int): offset to the end of the member in the parent file
        object.
    member_start_offset (int): offset to the start of the member in the parent
        file object.
    operating_system (int): type of file system on which the compression
        took place.
    original_filename (str): original filename of the uncompressed file.
    uncompressed_data_offset (int): offset of the start of the uncompressed
        data in this member relative to the whole gzip file's uncompressed data.
    uncompressed_data_size (int): total size of the data in this gzip member
        after decompression.
  """

  _DATA_TYPE_FABRIC_DEFINITION_FILE = os.path.join(
      os.path.dirname(__file__), 'gzip.yaml')

  with open(_DATA_TYPE_FABRIC_DEFINITION_FILE, 'rb') as file_object:
    _DATA_TYPE_FABRIC_DEFINITION = file_object.read()

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _MEMBER_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'gzip_member_header')

  _MEMBER_HEADER_SIZE = _MEMBER_HEADER.GetByteSize()

  _MEMBER_FOOTER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'gzip_member_footer')

  _MEMBER_FOOTER_SIZE = _MEMBER_FOOTER.GetByteSize()

  _UINT16LE = _DATA_TYPE_FABRIC.CreateDataTypeMap('uint16le')

  _UINT16LE_SIZE = _UINT16LE.GetByteSize()

  _CSTRING = _DATA_TYPE_FABRIC.CreateDataTypeMap('cstring')

  _GZIP_SIGNATURE = 0x8b1f

  _COMPRESSION_METHOD_DEFLATE = 8

  _FLAG_FTEXT = 0x01
  _FLAG_FHCRC = 0x02
  _FLAG_FEXTRA = 0x04
  _FLAG_FNAME = 0x08
  _FLAG_FCOMMENT = 0x10

  # The maximum size of the uncompressed data cache.
  _UNCOMPRESSED_DATA_CACHE_SIZE = 2 * 1024 * 1024

  def __init__(
      self, file_object, member_start_offset, uncompressed_data_offset):
    """Initializes a gzip member.

    Args:
      file_object (FileIO): file-like object, containing the gzip member.
      member_start_offset (int): offset to the beginning of the gzip member
          in the containing file.
      uncompressed_data_offset (int): current offset into the uncompressed data
          in the containing file.
    """
    self.comment = None
    self.modification_time = None
    self.operating_system = None
    self.original_filename = None

    # Offset into this member's uncompressed data of the first item in
    # the cache.
    self._cache_start_offset = None
    # Offset into this member's uncompressed data of the last item in
    # the cache.
    self._cache_end_offset = None
    self._cache = b''

    # Total size of the data in this gzip member after decompression.
    self.uncompressed_data_size = None
    # Offset of the start of the uncompressed data in this member relative to
    # the whole gzip file's uncompressed data.
    self.uncompressed_data_offset = uncompressed_data_offset

    # Offset to the start of the member in the parent file object.
    self.member_start_offset = member_start_offset

    # Initialize the member with data.
    self._file_object = file_object
    self._file_object.seek(self.member_start_offset, os.SEEK_SET)

    self._ReadMemberHeader(file_object)
    # Offset to the beginning of the compressed data in the file object.
    self._compressed_data_start = file_object.get_offset()

    self._decompressor_state = _GzipDecompressorState(
        self._compressed_data_start)

    self._LoadDataIntoCache(file_object, 0, read_all_data=True)

    self._ReadMemberFooter(file_object)

    # Offset to the end of the member in the parent file object.
    self.member_end_offset = file_object.get_offset()

  def _ReadMemberHeader(self, file_object):
    """Reads a member header.

    Args:
      file_object (FileIO): file-like object to read from.

    Raises:
      FileFormatError: if the member header cannot be read.
    """
    file_offset = file_object.tell()
    member_header = self._ReadStructure(
        file_object, file_offset, self._MEMBER_HEADER_SIZE,
        self._MEMBER_HEADER, 'member header')

    if member_header.signature != self._GZIP_SIGNATURE:
      raise errors.FileFormatError(
          'Unsupported signature: 0x{0:04x}.'.format(member_header.signature))

    if member_header.compression_method != self._COMPRESSION_METHOD_DEFLATE:
      raise errors.FileFormatError(
          'Unsupported compression method: {0:d}.'.format(
              member_header.compression_method))

    self.modification_time = member_header.modification_time
    self.operating_system = member_header.operating_system

    if member_header.flags & self._FLAG_FEXTRA:
      file_offset = file_object.tell()
      extra_field_data_size = self._ReadStructure(
          file_object, file_offset, self._UINT16LE_SIZE,
          self._UINT16LE, 'extra field data size')

      file_object.seek(extra_field_data_size, os.SEEK_CUR)

    if member_header.flags & self._FLAG_FNAME:
      file_offset = file_object.tell()
      string_value = self._ReadString(
          file_object, file_offset, self._CSTRING, 'original filename')

      self.original_filename = string_value.rstrip('\x00')

    if member_header.flags & self._FLAG_FCOMMENT:
      file_offset = file_object.tell()
      string_value = self._ReadString(
          file_object, file_offset, self._CSTRING, 'comment')

      self.comment = string_value.rstrip('\x00')

    if member_header.flags & self._FLAG_FHCRC:
      file_object.read(2)

  def _ReadMemberFooter(self, file_object):
    """Reads a member footer.

    Args:
      file_object (FileIO): file-like object to read from.

    Raises:
      FileFormatError: if the member footer cannot be read.
    """
    file_offset = file_object.tell()
    member_footer = self._ReadStructure(
        file_object, file_offset, self._MEMBER_FOOTER_SIZE,
        self._MEMBER_FOOTER, 'member footer')

    self.uncompressed_data_size = member_footer.uncompressed_data_size

  def _ResetDecompressorState(self):
    """Resets the state of the internal decompression object."""
    self._decompressor_state = _GzipDecompressorState(
        self._compressed_data_start)

  def FlushCache(self):
    """Empties the cache that holds cached decompressed data."""
    self._cache = b''
    self._cache_start_offset = None
    self._cache_end_offset = None
    self._ResetDecompressorState()

  def GetCacheSize(self):
    """Determines the size of the uncompressed cached data.

    Returns:
      int: number of cached bytes.
    """
    if not self._cache_start_offset or not self._cache_end_offset:
      return 0
    return self._cache_end_offset - self._cache_start_offset

  def IsCacheFull(self):
    """Checks whether the uncompressed data cache is full.

    Returns:
      bool: True if the cache is full.
    """
    return self.GetCacheSize() >= self._UNCOMPRESSED_DATA_CACHE_SIZE

  def ReadAtOffset(self, offset, size=None):
    """Reads a byte string from the gzip member at the specified offset.

    The function will read a byte string of the specified size or
    all of the remaining data if no size was specified.

    Args:
      offset (int): offset within the uncompressed data in this member to
        read from.
      size (Optional[int]): maximum number of bytes to read, where None
          represents all remaining data, to a maximum of the uncompressed
          cache size.

    Returns:
      bytes: data read.

    Raises:
      IOError: if the read failed.
      ValueError: if a negative read size or offset is specified.
    """
    if size is not None and size < 0:
      raise ValueError('Invalid size value {0!d}'.format(size))

    if offset < 0:
      raise ValueError('Invalid offset value {0!d}'.format(offset))

    if size == 0 or offset >= self.uncompressed_data_size:
      return b''

    if self._cache_start_offset is None:
      self._LoadDataIntoCache(self._file_object, offset)

    if offset > self._cache_end_offset or offset < self._cache_start_offset:
      self.FlushCache()
      self._LoadDataIntoCache(self._file_object, offset)

    cache_offset = offset - self._cache_start_offset
    if not size:
      return self._cache[cache_offset:]

    data_end_offset = cache_offset + size

    if data_end_offset > self._cache_end_offset:
      return self._cache[cache_offset:]

    return self._cache[cache_offset:data_end_offset]

  def _LoadDataIntoCache(
      self, file_object, minimum_offset, read_all_data=False):
    """Reads and decompresses the data in the member.

    This function already loads as much data as possible in the cache, up to
    UNCOMPRESSED_DATA_CACHE_SIZE bytes.

    Args:
      file_object (FileIO): file-like object.
      minimum_offset (int): offset into this member's uncompressed data at
          which the cache should start.
      read_all_data (bool): True if all the compressed data should be read
          from the member.
    """
    # Decompression can only be performed from beginning to end of the stream.
    # So, if data before the current position of the decompressor in the stream
    # is required, it's necessary to throw away the current decompression
    # state and start again.
    if minimum_offset < self._decompressor_state.uncompressed_offset:
      self._ResetDecompressorState()

    while not self.IsCacheFull() or read_all_data:
      decompressed_data = self._decompressor_state.Read(file_object)
      decompressed_data_length = len(decompressed_data)
      decompressed_end_offset = self._decompressor_state.uncompressed_offset
      decompressed_start_offset = (
          decompressed_end_offset - decompressed_data_length)

      data_to_add = decompressed_data
      added_data_start_offset = decompressed_start_offset

      if decompressed_start_offset < minimum_offset:
        data_to_add = None

      if decompressed_start_offset < minimum_offset < decompressed_end_offset:
        data_add_offset = decompressed_end_offset - minimum_offset
        data_to_add = decompressed_data[-data_add_offset]
        added_data_start_offset = decompressed_end_offset - data_add_offset

      if not self.IsCacheFull() and data_to_add:
        self._cache = b''.join([self._cache, data_to_add])
        if self._cache_start_offset is None:
          self._cache_start_offset = added_data_start_offset
        if self._cache_end_offset is None:
          self._cache_end_offset = self._cache_start_offset + len(data_to_add)
        else:
          self._cache_end_offset += len(data_to_add)

      # If there's no more data in the member, the unused_data value is
      # populated in the decompressor. When this situation arises, we rewind
      # to the end of the compressed_data section.
      unused_data = self._decompressor_state.GetUnusedData()
      if unused_data:
        seek_offset = -len(unused_data)
        file_object.seek(seek_offset, os.SEEK_CUR)
        self._ResetDecompressorState()
        break
