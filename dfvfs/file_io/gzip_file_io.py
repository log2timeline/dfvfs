# -*- coding: utf-8 -*-
"""The gzip file-like object."""

from __future__ import unicode_literals

import os

import construct

from dfvfs.lib import errors
from dfvfs.resolver import resolver
from dfvfs.compression import zlib_decompressor
from dfvfs.file_io import file_io


class GzipMember(object):
  """Single gzip member.

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
  _FILE_HEADER_STRUCT = construct.Struct(
      'file_header',
      construct.ULInt16('signature'),
      construct.UBInt8('compression_method'),
      construct.UBInt8('flags'),
      construct.SLInt32('modification_time'),
      construct.UBInt8('extra_flags'),
      construct.UBInt8('operating_system'))

  _FILE_FOOTER_STRUCT = construct.Struct(
      'file_footer',
      construct.ULInt32('checksum'),
      construct.ULInt32('uncompressed_data_size'))

  _FILE_SIGNATURE = 0x8b1f

  _COMPRESSION_METHOD_DEFLATE = 8

  _FLAG_FTEXT = 0x01
  _FLAG_FHCRC = 0x02
  _FLAG_FEXTRA = 0x04
  _FLAG_FNAME = 0x08
  _FLAG_FCOMMENT = 0x10

  _MAXIMUM_READ_SIZE = 1024 * 1024

  # The maximum size of the uncompressed data cache.
  _UNCOMPRESSED_DATA_CACHE_SIZE = 16 * 1024 * 1024

  def __init__(self, file_object, uncompressed_data_offset):
    """Initializes a file-like object.

    Args:
      file_object (FileIO): file-like object, positioned to the
          the beginning of the Gzip Member.
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
    self.member_start_offset = file_object.tell()
    # Offset to the end of the member in the parent file object.
    self.member_end_offset = None
    # Offset to the beginning of the compressed data in the file object.
    self._compressed_data_offset = None

    # Initialize the member with data
    self._file_object = file_object
    self._ReadHeader(file_object)
    self._LoadDataIntoCache(file_object, 0, read_all_data=True)
    self._ReadFooter(file_object)

  def GetCacheSize(self):
    """Gets the size of the uncompressed data cache.

    Returns:
      int: number of cached bytes.
    """
    if not self._cache_start_offset or not self._cache_end_offset:
      return 0
    return self._cache_end_offset - self._cache_start_offset

  def IsCacheFull(self):
    """Convenience method to check whether the uncompressed data cache is full.

    Returns:
      bool: True if the cache is full.
    """
    return self.GetCacheSize() >= self._UNCOMPRESSED_DATA_CACHE_SIZE

  def FlushCache(self):
    """Empties the cache that holds cached decompressed data."""
    self._cache = b''
    self._cache_start_offset = None
    self._cache_end_offset = None

  def ReadAtOffset(self, offset, size=None):
    """Reads a byte string from the file-like object at the specified offset.

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
    """
    if size is not None and size < 0:
      raise ValueError('Invalid size value smaller than zero.')

    if not self._cache_start_offset:
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
      minimum_offset (init): offset into this member's uncompressed data at
          which the cache should start.
      read_all_data (bool): whether to read all the compressed data from the
          member. Useful during the initial read, to locate the member footer.
    """
    # We always need to start from the beginning of the compressed data.
    file_object.seek(self._compressed_data_offset, os.SEEK_SET)
    decompressor = zlib_decompressor.DeflateDecompressor()
    current_offset = 0
    compressed_data = b''
    while not (self.IsCacheFull() and not read_all_data):
      compressed_data += file_object.read(self._MAXIMUM_READ_SIZE)
      decompressed_data, compressed_data = decompressor.Decompress(
          compressed_data)
      decompressed_data_length = len(decompressed_data)

      if current_offset >= minimum_offset:
        data_to_add = decompressed_data
        added_data_offset = current_offset
      elif current_offset + decompressed_data_length > minimum_offset:
        decompressed_data_offset = minimum_offset - current_offset
        data_to_add = decompressed_data[decompressed_data_offset:]
        added_data_offset = current_offset + decompressed_data_offset

      if not self.IsCacheFull() and data_to_add:
        self._cache = self._cache.join([data_to_add])
        if not self._cache_start_offset:
          self._cache_start_offset = added_data_offset
        if not self._cache_end_offset:
          self._cache_end_offset = self._cache_start_offset + len(data_to_add)
        else:
          self._cache_end_offset += len(data_to_add)

      current_offset += len(decompressed_data)

      # If there's no more data in the member, the unused_data value is
      # populated in the decompressor. When this situation arises, we rewind
      # to the end of the compressed_data section.
      unused_data = decompressor.unused_data
      if unused_data:
        seek_offset = -len(unused_data)
        file_object.seek(seek_offset, os.SEEK_CUR)
        break

  def _ReadHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object (FileIO): file-like object to read from.

    Raises:
      FileFormatError: if file format related errors are detected.
    """
    file_header = self._FILE_HEADER_STRUCT.parse_stream(file_object)
    self._compressed_data_offset = file_object.get_offset()

    if file_header.signature != self._FILE_SIGNATURE:
      raise errors.FileFormatError(
          'Unsupported file signature: 0x{0:04x}.'.format(
              file_header.signature))

    if file_header.compression_method != self._COMPRESSION_METHOD_DEFLATE:
      raise errors.FileFormatError(
          'Unsupported compression method: {0:d}.'.format(
              file_header.compression_method))

    self.modification_time = file_header.modification_time
    self.operating_system = file_header.operating_system

    if file_header.flags & self._FLAG_FEXTRA:
      extra_field_data_size = construct.ULInt16(
          'extra_field_data_size').parse_stream(file_object)
      file_object.seek(extra_field_data_size, os.SEEK_CUR)
      self._compressed_data_offset += 2 + extra_field_data_size

    if file_header.flags & self._FLAG_FNAME:
      # Since encoding is set construct will convert the C string to Unicode.
      # Note that construct 2 does not support the encoding to be a Unicode
      # string.
      self.original_filename = construct.CString(
          'original_filename', encoding=b'iso-8859-1').parse_stream(
              file_object)
      self._compressed_data_offset = file_object.get_offset()

    if file_header.flags & self._FLAG_FCOMMENT:
      # Since encoding is set construct will convert the C string to Unicode.
      # Note that construct 2 does not support the encoding to be a Unicode
      # string.
      self.comment = construct.CString(
          'comment', encoding=b'iso-8859-1').parse_stream(file_object)
      self._compressed_data_offset = file_object.get_offset()

    if file_header.flags & self._FLAG_FHCRC:
      self._compressed_data_offset += 2

  def _ReadFooter(self, file_object):
    """Reads the file footer.

    Args:
      file_object (FileIO): file-like object to read from.

    Raises:
      FileFormatError: if file format related errors are detected.
    """
    file_footer = self._FILE_FOOTER_STRUCT.parse_stream(file_object)
    self.uncompressed_data_size = file_footer.uncompressed_data_size
    self.member_end_offset = file_object.tell()


class GzipFile(file_io.FileIO):
  """File-like object of a gzip file.

  The gzip file format is defined in RFC1952: http://www.zlib.org/rfc-gzip.html

  Attributes:
    uncompressed_data_size (int): total size of the decompressed data stored
        in the gzip file.
  """

  def __init__(self, resolver_context):
    """Initializes a file-like object.

    Args:
      resolver_context (Context): resolver context.

    Raises:
      ValueError: when file_object is set.
    """
    super(GzipFile, self).__init__(resolver_context)
    self._compressed_data_size = -1
    self.uncompressed_data_size = 0
    self._current_offset = 0
    self._gzip_file_object = None
    self._members = []

  @property
  def original_filenames(self):
    """list(str): The original filenames stored in the gzip file."""
    return [member.original_filename for member in self._members]

  @property
  def modification_times(self):
    """list(int): The modification times stored in the gzip file."""
    return [member.modification_time for member in self._members]

  @property
  def operating_systems(self):
    """list(int): The operating system values stored in the gzip file."""
    return [member.operating_system for member in self._members]

  @property
  def comments(self):
    """list(str): The comments in the gzip file."""
    return [member.comment for member in self._members]

  def _GetMemberForOffset(self, offset):
    """Finds the member whose data includes the provided offset.

    Args:
      offset (int): offset in the uncompressed data to find the
          containing member for.

    Raises:
      ValueError: if the provided offset is outside of the bounds of the
      uncompressed data.
    """
    if offset < 0 or offset > self.uncompressed_data_size:
      raise ValueError('Offset {0:d} is larger that file size {1:d}.'.format(
          offset, self.uncompressed_data_size))

    for member in self._members:
      if (offset < member.uncompressed_data_offset +
          member.uncompressed_data_size):
        return member

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks to an offset within the file-like object.

    Args:
      offset (int): offset to seek to.
      whence (Optional(int)): value that indicates whether offset is an absolute
          or relative position within the file.

    Raises:
      IOError: if the seek failed or the file has not been opened.
    """
    if not self._gzip_file_object:
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

  def read(self, size=None):
    """Reads a byte string from the file-like object at the current offset.

    The function will read a byte string up to the specified size or
    all of the remaining data if no size was specified.

    Args:
      size (Optional[int]): number of bytes to read, where None is all
          remaining data.

    Returns:
      bytes: data read.

    Raises:
      IOError: if the read failed.
    """
    data = b''
    while (size and len(
        data) < size) and self._current_offset < self.uncompressed_data_size:
      member = self._GetMemberForOffset(self._current_offset)
      member_offset = self._current_offset - member.uncompressed_data_offset
      data_read = member.ReadAtOffset(member_offset, size)
      if data_read:
        self._current_offset += len(data_read)
        data = data.join([data_read])

    return data

  def get_offset(self):
    """Retrieves the current offset into the file-like object.

    Return:
      int: current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._gzip_file_object:
      raise IOError('Not opened.')
    return self._current_offset

  def get_size(self):
    """Retrieves the size of the file-like object.

    Returns:
      int: size of the file-like object data.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._gzip_file_object:
      raise IOError('Not opened.')
    return self.uncompressed_data_size

  def _Close(self):
    """Closes the file-like object."""
    self._members = []
    if self._gzip_file_object:
      self._gzip_file_object.close()

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
    if not path_spec:
      raise ValueError('Missing path specification.')

    if not path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    self._gzip_file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=self._resolver_context)
    self._gzip_file_object.seek(0, os.SEEK_SET)
    uncompressed_data_offset = 0
    while self._gzip_file_object.tell() < self._gzip_file_object.get_size():
      member = GzipMember(self._gzip_file_object, uncompressed_data_offset)
      uncompressed_data_offset = (
          uncompressed_data_offset + member.uncompressed_data_size)
      self.uncompressed_data_size += member.uncompressed_data_size
      self._members.append(member)
