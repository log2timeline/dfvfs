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
  """Implementation of a single gzip member."""
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

  _MAXIMUM_READ_SIZE = 10 * 2 ** 20  # 10 megabytes

  # The maximum size of the uncompressed data buffer.
  _UNCOMPRESSED_DATA_BUFFER_SIZE = 16 * 1024 * 1024

  def __init__(self, file_object, uncompressed_data_offset):
    """Initializes a file-like object.

    Args:
      file_object (FileIO): file-like object, positioned to the
          the beginning of the Gzip Member.
      uncompressed_data_offset (int): Current offset into the uncompressed data.

    Raises:
      ValueError: when file_object is set.
    """
    self.comment = None
    self.modification_time = None
    self.operating_system = None
    self.original_filename = None

    # Offset into the uncompressed data of the first item in the buffer.
    self._buffer_start_offset = None
    # Offset into the uncompressed data of the last item in the buffer.
    self._buffer_end_offset = None
    self._buffer = b''

    # Total size of the data in this gzip member after decompression.
    self.uncompressed_data_size = None
    # Offset of the data in this member relative the whole gzip uncompressed
    # data.
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
    self._ReadDataIntoBuffer(file_object)
    self._ReadFooter(file_object)

  @property
  def buffered_data_size(self):
    return self._buffer_end_offset - self._buffer_start_offset

  def FlushCache(self):
    """Empties the buffer that holds cached decompressed data."""
    self._TruncateBuffer(self.buffered_data_size)

  def read(self, offset, size=None):
    """Reads a byte string from the file-like object at the current offset.

    The function will read a byte string of the specified size or
    all of the remaining data if no size was specified.

    Args:
      offset (int): offset within the uncompressed data to read from.
      size (Optional[int]): maximum number of bytes to read, where None
          represents all remaining data.

    Returns:
      bytes: data read.

    Raises:
      IOError: if the read failed.
    """
    if size is not None and size < 0:
      raise ValueError('Invalid size value smaller than zero.')

    if offset > self._buffer_start_offset:
      self._TruncateBuffer()
      self._ReadDataIntoBuffer(self._file_object, offset=offset)

    if not self.buffered_data_size > = size:
      self._ReadDataIntoBuffer(self._file_object)
    if not size:
      data = self._buffer[self.uncompressed_data_offset:]
      self.uncompressed_data_offset = self.uncompressed_data_size
    else:
      end = self.uncompressed_data_offset + size
      data = self._buffer[self.uncompressed_data_offset:end]
      self.uncompressed_data_offset = end
    return data

  def get_offset(self):
    """Retrieves the current offset into the member.

    Return:
      int: current offset into the file-like object.
    """
    return self.uncompressed_data_offset

  def _TruncateBuffer(self, length=None):
    """

    Args:
      length (int): number of bytes to truncate from the buffer.
    """
    if length is None:
      self._buffer = []
      self._buffer_start_offset = None
      self._buffer_end_offset = None
      return

    if length > self.buffered_data_size:
      raise ValueError('Invalid length greater than cached data.')
    self._buffer = self._buffer[length:]
    self._buffer_start_offset -= length

  def _ReadDataIntoBuffer(self, file_object, offset):
    """Reads and decompresses the data in the member.

    Args:
      file_object (FileIO): file-like object.
      offset (init): offset into this member's uncompressed data.
    """
    # We always need to start from the beginning of the compressed data.
    file_object.seek(self._compressed_data_offset, os.SEEK_SET)
    decompressor = zlib_decompressor.DeflateDecompressor()
    current_offset = 0
    compressed_data = b''
    while not self.buffered_data_size >= self._UNCOMPRESSED_DATA_BUFFER_SIZE:
      compressed_data += file_object.read(self._MAXIMUM_READ_SIZE)
      decompressed_data, compressed_data = decompressor.Decompress(
          compressed_data)
      # Only add to buffer if the offset has been reached.
      if offset < current_offset + len(decompressed_data):
        data_to_buffer = decompressed_data[offset - current_offset:]
        self._buffer += data_to_buffer
        if not self._buffer_start_offset:
          buffer_start_offset = current_offset +

      # Check if we're at the end of the stream.
      unused_data = decompressor.unused_data
      if unused_data:
        seek_offset = -len(unused_data)
        file_object.seek(seek_offset, os.SEEK_CUR)
        break

  def _ReadDataIntoBufferOld(self, file_object):
    """Reads and decompresses the data in the member.

    Args:
      file_object (FileIO): file-like object.
    """
    # We always need to start from the beginning of the compressed data.
    file_object.seek(self._compressed_data_offset, os.SEEK_SET)
    decompressor = zlib_decompressor.DeflateDecompressor()
    completed = False
    compressed_data = b''
    while not completed:
      compressed_data += file_object.read(self._MAXIMUM_READ_SIZE)
      decompressed_data, compressed_data = decompressor.Decompress(
          compressed_data)
      self._buffer += data_to_buffer
      unused_data = decompressor.unused_data
      if unused_data:
        completed = True
        seek_offset = -len(unused_data)
        file_object.seek(seek_offset, os.SEEK_CUR)

    self.cached = True
    self.uncompressed_data_size = len(self._buffer)

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
  """

  _MAXMIUM_DATA_BUFFER_SIZE = 200 * 1024 ** 2

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
    return [member.original_filename for member in self._members]

  @property
  def modification_times(self):
    return [member.modification_time for member in self._members]

  @property
  def operating_systems(self):
    return [member.operating_system for member in self._members]

  @property
  def comments(self):
    return [member.comment for member in self._members]

  def _GetMemberForOffset(self, offset):
    """Finds the member """
    for member in self._members:
      if offset < member.uncompressed_data_offset + member.uncompressed_data_size:
        return member

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks to an offset within the file-like object.

    Args:
      offset (int): offset to seek to.
      whence (Optional(int)): value that indicates whether offset is an absolute
          or relative position within the file.

    Raises:
      IOError: if the seek failed.
    """
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
    while len(data) < size and self._current_offset < self.uncompressed_data_size:
      member = self._GetMemberForOffset(self._current_offset)
      member_offset = self._current_offset - member.uncompressed_data_offset
      member.seek(member_offset)
      data_read = member.read(size)
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
    return self._current_offset

  def get_size(self):
    """Retrieves the size of the file-like object.

    Returns:
      int: size of the file-like object data.

    Raises:
      IOError: if the file-like object has not been opened.
    """
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
