# -*- coding: utf-8 -*-
"""The gzip file-like object."""

import os

import construct

from dfvfs.file_io import file_object_io
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import compressed_stream_path_spec
from dfvfs.path import data_range_path_spec
from dfvfs.resolver import resolver


class GzipFile(file_object_io.FileObjectIO):
  """Class that implements a file-like object of a gzip file.

     The gzip file is a zlib compressed data stream with additional metadata.
  """
  _FILE_HEADER_STRUCT = construct.Struct(
      u'file_header',
      construct.ULInt16(u'signature'),
      construct.UBInt8(u'compression_method'),
      construct.UBInt8(u'flags'),
      construct.SLInt32(u'modification_time'),
      construct.UBInt8(u'extra_flags'),
      construct.UBInt8(u'operating_system'))

  _FILE_FOOTER_STRUCT = construct.Struct(
      u'file_footer',
      construct.ULInt32(u'checksum'),
      construct.ULInt32(u'uncompressed_data_size'))

  _FILE_SIGNATURE = 0x8b1f

  _COMPRESSION_METHOD_DEFLATE = 8

  _FLAG_FTEXT = 0x01
  _FLAG_FHCRC = 0x02
  _FLAG_FEXTRA = 0x04
  _FLAG_FNAME = 0x08
  _FLAG_FCOMMENT = 0x10

  def __init__(self, resolver_context, file_object=None):
    """Initializes the file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      file_object: optional file-like object.

    Raises:
      ValueError: when file_object is set.
    """
    if file_object:
      raise ValueError(u'File object value set.')

    super(GzipFile, self).__init__(resolver_context)
    self._compressed_data_offset = -1
    self._compressed_data_size = -1
    self.comment = None
    self.modification_time = None
    self.operating_system = None
    self.original_filename = None
    self.uncompressed_data_size = 0

  def _ReadFileHeader(self, file_object):
    """Reads the file header.

    Args:
      file_object: the file-like object to read from.

    Raises:
      FileFormatError: if file format related errors are detected.
    """
    file_object.seek(0, os.SEEK_SET)
    file_header = self._FILE_HEADER_STRUCT.parse_stream(file_object)
    self._compressed_data_offset = file_object.get_offset()

    if file_header.signature != self._FILE_SIGNATURE:
      raise errors.FileFormatError(
          u'Unsuppored file signature: 0x{0:04x}.'.format(
              file_header.signature))

    if file_header.compression_method != self._COMPRESSION_METHOD_DEFLATE:
      raise errors.FileFormatError(
          u'Unsuppored compression method: {0:d}.'.format(
              file_header.compression_method))

    self.modification_time = file_header.modification_time
    self.operating_system = file_header.operating_system

    if file_header.flags & self._FLAG_FEXTRA:
      extra_field_data_size = construct.ULInt16(
          u'extra_field_data_size').parse_stream(file_object)
      file_object.seek(extra_field_data_size, os.SEEK_CUR)
      self._compressed_data_offset += 2 + extra_field_data_size

    if file_header.flags & self._FLAG_FNAME:
      # Since encoding is set construct will convert the C string to Unicode.
      # Note that construct 2 does not support the encoding to be a Unicode
      # string.
      self.original_filename = construct.CString(
          u'original_filename', encoding='iso-8859-1').parse_stream(
              file_object)
      self._compressed_data_offset = file_object.get_offset()

    if file_header.flags & self._FLAG_FCOMMENT:
      # Since encoding is set construct will convert the C string to Unicode.
      # Note that construct 2 does not support the encoding to be a Unicode
      # string.
      self.comment = construct.CString(
          u'comment', encoding='iso-8859-1').parse_stream(file_object)
      self._compressed_data_offset = file_object.get_offset()

    if file_header.flags & self._FLAG_FHCRC:
      self._compressed_data_offset += 2

    self._compressed_data_size = (
        file_object.get_size() - (self._compressed_data_offset + 8))

  def _ReadFileFooter(self, file_object):
    """Reads the file footer.

    Args:
      file_object: the file-like object to read from.

    Raises:
      FileFormatError: if file format related errors are detected.
    """
    file_object.seek(-8, os.SEEK_END)
    file_footer = self._FILE_FOOTER_STRUCT.parse_stream(file_object)

    self.uncompressed_data_size = file_footer.uncompressed_data_size

  def _OpenFileObject(self, path_spec):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: optional the path specification (instance of PathSpec).

    Returns:
      A file-like object.
    """
    gzip_file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=self._resolver_context)

    try:
      self._ReadFileHeader(gzip_file_object)
      self._ReadFileFooter(gzip_file_object)

    finally:
      gzip_file_object.close()

    path_spec_data_range = data_range_path_spec.DataRangePathSpec(
        range_offset=self._compressed_data_offset,
        range_size=self._compressed_data_size, parent=path_spec.parent)
    path_spec_compressed_stream = (
        compressed_stream_path_spec.CompressedStreamPathSpec(
            compression_method=definitions.COMPRESSION_METHOD_DEFLATE,
            parent=path_spec_data_range))

    return resolver.Resolver.OpenFileObject(
        path_spec_compressed_stream, resolver_context=self._resolver_context)
