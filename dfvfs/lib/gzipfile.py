# -*- coding: utf-8 -*-
"""Gzip compressed stream file."""

# Note: do not rename file to gzip.py this can cause the exception:
# AttributeError: 'module' object has no attribute 'GzipFile'
# when using pip.

import collections
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
    uncompressed_offset (int): offset into the uncompressed data in a gzip
        member last emitted by the state object.
  """

  _MAXIMUM_READ_SIZE = 16 * 1024 * 1024

  def __init__(self, stream_start):
    """Initializes a gzip member decompressor wrapper.

    Args:
      stream_start (int): offset to the compressed stream within the containing
          file object.
    """
    self._compressed_data = b''
    self._decompressor = zlib_decompressor.DeflateDecompressor()
    self._last_read = stream_start
    self.uncompressed_offset = 0

  def Read(self, file_object):
    """Reads the next uncompressed data from the gzip stream.

    Args:
      file_object (FileIO): file object that contains the compressed stream.

    Returns:
      bytes: next uncompressed data from the compressed stream.
    """
    file_object.seek(self._last_read, os.SEEK_SET)
    read_data = file_object.read(self._MAXIMUM_READ_SIZE)
    self._last_read = file_object.get_offset()

    compressed_data = b''.join([self._compressed_data, read_data])
    decompressed_data, remaining_compressed_data = (
        self._decompressor.Decompress(compressed_data))

    self._compressed_data = remaining_compressed_data
    self.uncompressed_offset += len(decompressed_data)
    return decompressed_data

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
      os.path.dirname(__file__), 'gzipfile.yaml')

  with open(_DATA_TYPE_FABRIC_DEFINITION_FILE, 'rb') as file_object:
    _DATA_TYPE_FABRIC_DEFINITION = file_object.read()

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _MEMBER_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'gzip_member_header')

  _MEMBER_FOOTER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'gzip_member_footer')

  _UINT16LE = _DATA_TYPE_FABRIC.CreateDataTypeMap('uint16le')

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
      uncompressed_data_offset (int): offset of the start of the uncompressed
          data in this member relative to the whole gzip file's uncompressed
          data.
    """
    self._cache = b''
    # End offset of the cached uncompressed data of the member.
    self._cache_end_offset = None
    # Start offset of the cached uncompressed data of the member.
    self._cache_start_offset = None

    self.comment = None
    self.modification_time = None
    self.operating_system = None
    self.original_filename = None

    file_size = file_object.get_size()

    file_object.seek(member_start_offset, os.SEEK_SET)
    self._ReadMemberHeader(file_object)

    data_offset = 0
    uncompressed_data_size = 0

    compressed_data_offset = file_object.get_offset()
    decompressor_state = _GzipDecompressorState(compressed_data_offset)

    # Read the member data to determine the uncompressed data size and
    # the offset of the member footer.
    file_offset = compressed_data_offset
    while file_offset < file_size:
      data_offset += uncompressed_data_size

      decompressed_data = decompressor_state.Read(file_object)
      uncompressed_data_size += len(decompressed_data)

      # Note that unused data will be set when the decompressor reads beyond
      # the end of the compressed data stream.
      unused_data = decompressor_state.GetUnusedData()
      if unused_data:
        file_object.seek(-len(unused_data), os.SEEK_CUR)
        file_offset = file_object.get_offset()
        break

      file_offset = file_object.get_offset()

    # Do not read the the last member footer if it is missing, which is
    # a common corruption scenario.
    if file_offset < file_size:
      self._ReadStructureFromFileObject(
          file_object, file_offset, self._MEMBER_FOOTER)

    member_end_offset = file_object.get_offset()

    # Initialize the member with data.
    self._file_object = file_object
    self._file_object.seek(member_start_offset, os.SEEK_SET)

    # Cache uncompressed data of gzip files that fit entirely in the cache.
    if (data_offset == 0 and
        uncompressed_data_size < self._UNCOMPRESSED_DATA_CACHE_SIZE):
      self._cache = decompressed_data
      self._cache_start_offset = 0
      self._cache_end_offset = uncompressed_data_size

    # Offset to the beginning of the compressed data in the file object.
    self._compressed_data_start = compressed_data_offset
    self._decompressor_state = _GzipDecompressorState(compressed_data_offset)

    # Offset to the start of the member in the parent file object.
    self.member_start_offset = member_start_offset

    # Offset to the end of the member in the parent file object.
    self.member_end_offset = member_end_offset

    # Total size of the data in this gzip member after decompression.
    self.uncompressed_data_size = uncompressed_data_size

    # Offset of the start of the uncompressed data in this member relative to
    # the whole gzip file's uncompressed data.
    self.uncompressed_data_offset = uncompressed_data_offset

  def _GetCacheSize(self):
    """Determines the size of the uncompressed cached data.

    Returns:
      int: number of cached bytes.
    """
    if None in (self._cache_start_offset, self._cache_end_offset):
      return 0

    return self._cache_end_offset - self._cache_start_offset

  def _IsCacheFull(self):
    """Checks whether the uncompressed data cache is full.

    Returns:
      bool: True if the cache is full.
    """
    return self._GetCacheSize() >= self._UNCOMPRESSED_DATA_CACHE_SIZE

  def _LoadDataIntoCache(self, file_object, minimum_offset):
    """Reads and decompresses the data in the member.

    This function already loads as much data as possible in the cache, up to
    UNCOMPRESSED_DATA_CACHE_SIZE bytes.

    Args:
      file_object (FileIO): file-like object.
      minimum_offset (int): offset into this member's uncompressed data at
          which the cache should start.
    """
    # Decompression can only be performed from beginning to end of the stream.
    # So, if data before the current position of the decompressor in the stream
    # is required, it's necessary to throw away the current decompression
    # state and start again.
    if minimum_offset < self._decompressor_state.uncompressed_offset:
      self._ResetDecompressorState()

    cache_is_full = self._IsCacheFull()
    while not cache_is_full:
      decompressed_data = self._decompressor_state.Read(file_object)
      # Note that decompressed_data will be empty if there is no data left
      # to read and decompress.
      if not decompressed_data:
        break

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
        data_to_add = decompressed_data[-data_add_offset:]
        added_data_start_offset = decompressed_end_offset - data_add_offset

      if data_to_add and not cache_is_full:
        self._cache = b''.join([self._cache, data_to_add])
        if self._cache_start_offset is None:
          self._cache_start_offset = added_data_start_offset
        if self._cache_end_offset is None:
          self._cache_end_offset = self._cache_start_offset + len(data_to_add)
        else:
          self._cache_end_offset += len(data_to_add)

        cache_is_full = self._IsCacheFull()

      # If there's no more data in the member, the unused_data value is
      # populated in the decompressor. When this situation arises, we rewind
      # to the end of the compressed_data section.
      unused_data = self._decompressor_state.GetUnusedData()
      if unused_data:
        seek_offset = -len(unused_data)
        file_object.seek(seek_offset, os.SEEK_CUR)
        self._ResetDecompressorState()
        break

  def _ReadMemberHeader(self, file_object):
    """Reads a member header.

    Args:
      file_object (FileIO): file-like object to read from.

    Raises:
      FileFormatError: if the member header cannot be read.
    """
    file_offset = file_object.get_offset()
    member_header, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, self._MEMBER_HEADER)

    if member_header.signature != self._GZIP_SIGNATURE:
      raise errors.FileFormatError(
          f'Unsupported signature: 0x{member_header.signature:04x}.')

    if member_header.compression_method != self._COMPRESSION_METHOD_DEFLATE:
      raise errors.FileFormatError((
          f'Unsupported compression method: '
          f'{member_header.compression_method:d}.'))

    self.modification_time = member_header.modification_time
    self.operating_system = member_header.operating_system

    if member_header.flags & self._FLAG_FEXTRA:
      file_offset = file_object.get_offset()
      extra_field_data_size, _ = self._ReadStructureFromFileObject(
          file_object, file_offset, self._UINT16LE)

      file_object.seek(extra_field_data_size, os.SEEK_CUR)

    if member_header.flags & self._FLAG_FNAME:
      file_offset = file_object.get_offset()
      self.original_filename, _ = self._ReadStructureFromFileObject(
          file_object, file_offset, self._CSTRING)

    if member_header.flags & self._FLAG_FCOMMENT:
      file_offset = file_object.get_offset()
      self.comment, _ = self._ReadStructureFromFileObject(
          file_object, file_offset, self._CSTRING)

    if member_header.flags & self._FLAG_FHCRC:
      file_object.read(2)

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
      raise ValueError(f'Unsupported size value: {size!s}')

    if offset < 0:
      raise ValueError(f'Unsupported offset value: {offset!s}')

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


class GzipCompressedStream(object):
  """File-like object of a gzip compressed stream (file).

  The gzip file format is defined in RFC1952: http://www.zlib.org/rfc-gzip.html

  Attributes:
    uncompressed_data_size (int): total size of the decompressed data stored
        in the gzip file.
  """

  def __init__(self):
    """Initializes a file-like object."""
    super(GzipCompressedStream, self).__init__()
    self._compressed_data_size = -1
    self._current_offset = 0
    self._file_object = None
    self._members_by_end_offset = collections.OrderedDict()

    self.uncompressed_data_size = 0

  @property
  def members(self):
    """list(GzipMember): members in the gzip file."""
    return list(self._members_by_end_offset.values())

  def _GetMemberForOffset(self, offset):
    """Finds the member whose data includes the provided offset.

    Args:
      offset (int): offset in the uncompressed data to find the
          containing member for.

    Returns:
      GzipMember: gzip file member or None if not available.

    Raises:
      ValueError: if the provided offset is outside of the bounds of the
          uncompressed data.
    """
    if offset < 0 or offset >= self.uncompressed_data_size:
      raise ValueError((
          f'Offset: {offset:d} is larger than file size: '
          f'{self.uncompressed_data_size:d}.'))

    for end_offset, member in self._members_by_end_offset.items():
      if offset < end_offset:
        return member

    return None

  def Open(self, file_object):
    """Opens the file-like object defined by path specification.

    Args:
      file_object (FileIO): file-like object that contains the gzip compressed
          stream.

    Raises:
      IOError: if the file-like object could not be opened.
      OSError: if the file-like object could not be opened.
    """
    file_size = file_object.get_size()

    file_object.seek(0, os.SEEK_SET)

    uncompressed_data_offset = 0
    next_member_offset = 0

    while next_member_offset < file_size:
      member = GzipMember(
          file_object, next_member_offset, uncompressed_data_offset)
      uncompressed_data_offset = (
          uncompressed_data_offset + member.uncompressed_data_size)
      self._members_by_end_offset[uncompressed_data_offset] = member
      self.uncompressed_data_size += member.uncompressed_data_size
      next_member_offset = member.member_end_offset

    self._file_object = file_object

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.
  # pylint: disable=invalid-name

  def close(self):
    """Closes the file-like object."""
    self._members_by_end_offset = []
    if self._file_object:
      self._file_object = None

  def read(self, size=None):
    """Reads a byte string from the gzip file at the current offset.

    The function will read a byte string up to the specified size or
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
    data = b''
    while ((size and len(data) < size) and
           self._current_offset < self.uncompressed_data_size):
      member = self._GetMemberForOffset(self._current_offset)
      member_offset = self._current_offset - member.uncompressed_data_offset

      data_read = member.ReadAtOffset(member_offset, size)
      if not data_read:
        break

      self._current_offset += len(data_read)
      data = b''.join([data, data_read])

    return data

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks to an offset within the file-like object.

    Args:
      offset (int): offset to seek to.
      whence (Optional(int)): value that indicates whether offset is an absolute
          or relative position within the file.

    Raises:
      IOError: if the seek failed or the file has not been opened.
      OSError: if the seek failed or the file has not been opened.
    """
    if not self._file_object:
      raise IOError('Not opened.')

    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self.uncompressed_data_size
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
    if not self._file_object:
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
    if not self._file_object:
      raise IOError('Not opened.')

    return self.uncompressed_data_size
