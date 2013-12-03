#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The PyVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The gzip file-like object."""

import construct
import os

from pyvfs.io import compressed_stream
from pyvfs.io import file_io
from pyvfs.lib import definitions
from pyvfs.lib import errors
from pyvfs.path import compressed_stream_path_spec
from pyvfs.path import data_range_path_spec
from pyvfs.resolver import resolver


class GzipFile(file_io.FileIO):
  """Class that implements a file-like object of a gzip file.

     The gzip file is a zlib compressed data stream with additional metadata.
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

  def __init__(self):
    """Initializes the file-like object."""
    super(GzipFile, self).__init__()
    self._file_object = None
    self._compressed_data_offset = -1
    self._compressed_data_size = -1
    self._uncompressed_data_size = -1
    self.comment = None
    self.modification_time = None
    self.operating_system = None
    self.original_filename = None

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
          'extra_field_data_size').parse_stream(file_object)
      file_object.seek(extra_field_data_size, os.SEEK_CUR)
      self._compressed_data_offset += 2 + extra_field_data_size

    if file_header.flags & self._FLAG_FNAME:
      # Since encoding is set construct will convert the C string to Unicode.
      self.original_filename = construct.CString(
          'original_filename', encoding='iso-8859-1').parse_stream(file_object)
      self._compressed_data_offset = file_object.get_offset()

    if file_header.flags & self._FLAG_FCOMMENT:
      # Since encoding is set construct will convert the C string to Unicode.
      self.comment = construct.CString(
          'comment', encoding='iso-8859-1').parse_stream(file_object)
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

    self._uncompressed_data_size = file_footer.uncompressed_data_size

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.

  def open(self, path_spec, mode='rb'):
    """Opens the file-like object.

    Args:
      path_spec: the path specification (instance of path.PathSpec).

    Raises:
      IOError: if the open file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification or mode is invalid.
    """
    if not path_spec:
      raise ValueError(u'Missing path specfication.')

    if mode != 'rb':
      raise ValueError(u'Unsupport mode: {0:s}.'.format(mode))

    if self._file_object:
      raise IOError(u'Already open.')

    file_object = resolver.Resolver.OpenPathSpec(path_spec)

    self._ReadFileHeader(file_object)
    self._ReadFileFooter(file_object)

    file_object.close()

    path_spec_data_range = data_range_path_spec.DataRangePathSpec(
        self._compressed_data_offset, self._compressed_data_size,
        parent=path_spec)
    path_spec_compressed_stream = (
        compressed_stream_path_spec.CompressedStreamPathSpec(
            definitions.COMPRESSION_METHOD_DEFLATE,
            parent=path_spec_data_range))

    self._file_object = compressed_stream.CompressedStream()
    self._file_object.SetUncompressedStreamSize(self._uncompressed_data_size)
    self._file_object.open(path_spec_compressed_stream)

  def close(self):
    """Closes the file-like object.

       If the file-like object was passed in the init function
       the data range file-like object does not control the file-like object
       and should not actually close it.

    Raises:
      IOError: if the close failed.
    """
    if not self._file_object:
      raise IOError(u'Not opened.')

    self._file_object.close()

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
    if not self._file_object:
      raise IOError(u'Not opened.')

    return self._file_object.read(size)

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks an offset within the file-like object.

    Args:
      offset: the offset to seek.
      whence: optional value that indicates whether offset is an absolute
              or relative position within the file. Default is SEEK_SET.

    Raises:
      IOError: if the seek failed.
    """
    if not self._file_object:
      raise IOError(u'Not opened.')

    return self._file_object.seek(offset, whence)

  def get_offset(self):
    """Returns the current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._file_object:
      raise IOError(u'Not opened.')

    return self._file_object.get_offset()

  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._file_object:
      raise IOError(u'Not opened.')

    return self._file_object.get_size()
