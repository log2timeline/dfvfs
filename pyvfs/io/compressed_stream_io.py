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
"""The compressed stream file-like object implementation."""

import abc
import bz2
import os
import zlib

from pyvfs.io import file_io
from pyvfs.lib import definitions
from pyvfs.lib import errors
from pyvfs.resolver import resolver


class _Decompressor(object):
  """Class that implements the decompressor object interface."""

  @abc.abstractmethod
  def Decompress(self, compressed_data):
    """Decompresses the compressed data.

    Args:
      compressed_data: a byte string containing the compressed data.

    Returns:
      A tuple containing a byte string of the uncompressed data and
      the remaining compressed data.
    """


class _Bzip2Decompressor(_Decompressor):
  """Class that implements a BZIP2 decompressor using bz2."""

  def __init__(self):
    """Initializes the decompressor object."""
    super(_Bzip2Decompressor, self).__init__()
    self._bz2_decompressor = bz2.BZ2Decompressor()

  def Decompress(self, compressed_data):
    """Decompresses the compressed data.

    Args:
      compressed_data: a byte string containing the compressed data.

    Returns:
      A tuple containing a byte string of the uncompressed data and
      the remaining compressed data.
    """
    uncompressed_data = self._bz2_decompressor.decompress(compressed_data)
    remaining_compressed_data = getattr(
        self._bz2_decompressor, 'unused_data', '')

    return (uncompressed_data, remaining_compressed_data)


class _ZlibDecompressor(_Decompressor):
  """Class that implements a "zlib DEFLATE" decompressor using zlib."""

  def __init__(self, window_size=zlib.MAX_WBITS):
    """Initializes the decompressor object.

    Args:
      window_size: optional base two logarithm of the size of the compression
                   history buffer (aka window size). The default is
                   zlib.MAX_WBITS. When the value is negative, the standard
                   zlib data header is suppressed.
    """
    super(_ZlibDecompressor, self).__init__()
    self._zlib_decompressor = zlib.decompressobj(window_size)

  def Decompress(self, compressed_data):
    """Decompresses the compressed data.

    Args:
      compressed_data: a byte string containing the compressed data.

    Returns:
      A tuple containing a byte string of the uncompressed data and
      the remaining compressed data.
    """
    uncompressed_data = self._zlib_decompressor.decompress(compressed_data)
    remaining_compressed_data = getattr(
        self._zlib_decompressor, 'unused_data', '')

    return (uncompressed_data, remaining_compressed_data)


class _DeflateDecompressor(_ZlibDecompressor):
  """Class that implements a "raw DEFLATE" decompressor using zlib."""

  def __init__(self):
    """Initializes the decompressor object."""
    super(_DeflateDecompressor, self).__init__(window_size=-zlib.MAX_WBITS)


class CompressedStream(file_io.FileIO):
  """Class that implements a file-like object of a compressed stream."""

  # The size of the compressed data buffer.
  _COMPRESSED_DATA_BUFFER_SIZE = 8 * 1024 * 1024

  def __init__(self, compression_method=None, file_object=None):
    """Initializes the file-like object.

       If the file-like object is chained do not separately use the parent
       file-like object.

    Args:
      compression_method: optional method used to the compress the data.
      file_object: optional parent file-like object. The default is None.

    Raises:
      ValueError: if file_object provided but compression_method is not.
    """
    if file_object is not None and compression_method is None:
      raise ValueError(
          u'File-like object provided without corresponding compression '
          u'method.')

    super(CompressedStream, self).__init__()
    self._compression_method = compression_method
    self._file_object = file_object
    self._compressed_data = ''
    self._current_offset = 0
    self._decompressor = None
    self._realign_offset = True
    self._uncompressed_data = ''
    self._uncompressed_data_offset = 0
    self._uncompressed_data_size = 0
    self._uncompressed_stream_size = None

    if file_object:
      self._file_object_set_in_init = True
    else:
      self._file_object_set_in_init = False
    self._is_open = False

  def _GetDecompressor(self):
    """Retrieves the decompressor."""
    if self._compression_method == definitions.COMPRESSION_METHOD_BZIP2:
      return _Bzip2Decompressor()

    elif self._compression_method == definitions.COMPRESSION_METHOD_DEFLATE:
      return _DeflateDecompressor()

    elif self._compression_method == definitions.COMPRESSION_METHOD_ZLIB:
      return _ZlibDecompressor()

    return

  def _GetUncompressedStreamSize(self):
    """Retrieves the uncompressed stream size."""
    self._file_object.seek(0, os.SEEK_SET)

    self._decompressor = self._GetDecompressor()
    self._uncompressed_data = ''

    compressed_data_offset = 0
    compressed_data_size = self._file_object.get_size()
    uncompressed_stream_size = 0

    while compressed_data_offset < compressed_data_size:
      read_count = self._ReadCompressedData(self._COMPRESSED_DATA_BUFFER_SIZE)

      compressed_data_offset += read_count
      uncompressed_stream_size += self._uncompressed_data_size

    return uncompressed_stream_size

  def _AlignUncompressedDataOffset(self, uncompressed_data_offset):
    """Aligns the compressed file with the uncompressed data offset.

    Args:
      uncompressed_data_offset: the uncompressed data offset.
    """
    self._file_object.seek(0, os.SEEK_SET)

    self._decompressor = self._GetDecompressor()
    self._uncompressed_data = ''

    compressed_data_offset = 0
    compressed_data_size = self._file_object.get_size()

    while compressed_data_offset < compressed_data_size:
      read_count = self._ReadCompressedData(self._COMPRESSED_DATA_BUFFER_SIZE)

      compressed_data_offset += read_count

      if uncompressed_data_offset < self._uncompressed_data_size:
        self._uncompressed_data_offset = uncompressed_data_offset
        break

      uncompressed_data_offset -= self._uncompressed_data_size

  def _ReadCompressedData(self, read_size):
    """Reads compressed data from the file-like object.

    Args:
      read_size: the number of bytes of compressed data to read.

    Returns:
      The number of bytes of compressed data read.
    """
    compressed_data = self._file_object.read(read_size)

    read_count = len(compressed_data)

    self._compressed_data = ''.join([self._compressed_data, compressed_data])

    self._uncompressed_data, self._compressed_data = (
        self._decompressor.Decompress(self._compressed_data))

    self._uncompressed_data_size = len(self._uncompressed_data)

    return read_count

  def SetUncompressedStreamSize(self, uncompressed_stream_size):
    """Sets the uncompressed stream size.

       This function is used to set the uncompressed stream size if it can be
       determined separately.

    Args:
      uncompressed_stream_size: the size of the uncompressed stream in bytes.

    Raises:
      IOError: if the file-like object is already open.
      ValueError: if the uncompressed stream size is invalid.
    """
    if self._is_open:
      raise IOError(u'Already open.')

    if uncompressed_stream_size < 0:
      raise ValueError((
          u'Invalid uncompressed stream size: {0:d} value out of '
          u'bounds.').format(uncompressed_stream_size))

    self._uncompressed_stream_size = uncompressed_stream_size

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.

  def open(self, path_spec=None, mode='rb'):
    """Opens the file-like object.

    Args:
      path_spec: optional path specification (instance of PathSpec),
                 the default is None.
      mode: the file access mode, the default is 'rb' read-only binary.

    Raises:
      IOError: if the open file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification or mode is invalid.
    """
    if not self._file_object_set_in_init and not path_spec:
      raise ValueError(u'Missing path specfication.')

    if mode != 'rb':
      raise ValueError(u'Unsupport mode: {0:s}.'.format(mode))

    if self._is_open:
      raise IOError(u'Already open.')

    if not self._file_object_set_in_init:
      if not path_spec.HasParent():
        raise errors.PathSpecError(
            u'Unsupported path specification without parent.')

      self._compression_method = getattr(path_spec, 'compression_method', None)

      if self._compression_method is None:
        raise errors.PathSpecError(
            u'Path specification missing compression method.')

      self._file_object = resolver.Resolver.OpenFileObject(path_spec.parent)

    self._is_open = True

  def close(self):
    """Closes the file-like object.

       If the file-like object was passed in the init function
       the compressed stream file-like object does not control
       the file-like object and should not actually close it.

    Raises:
      IOError: if the close failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if not self._file_object_set_in_init:
      self._file_object.close()
      self._file_object = None

    self._compressed_data = ''
    self._decompressor = None
    self._uncompressed_data = ''
    self._is_open = False

  def read(self, size=None):
    """Reads a byte string from the file-like object at the current offset.

       The function will read a byte string of the specified size or
       all of the remaining data if no size was specified.

    Args:
      size: Optional integer value containing the number of bytes to read.
            Default is all remaining data (None).

    Returns:
      A byte string containing the data read.

    Raises:
      IOError: if the read failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if self._current_offset < 0:
      raise IOError(
          u'Invalid current offset: {0:d} value less than zero.'.format(
              self._current_offset))

    if self._uncompressed_stream_size is None:
      self._uncompressed_stream_size = self._GetUncompressedStreamSize()

    if self._uncompressed_stream_size < 0:
      raise IOError(u'Invalid uncompressed stream size.')

    if self._current_offset >= self._uncompressed_stream_size:
      return ''

    if size is None:
      size = self._uncompressed_stream_size
    if self._current_offset + size > self._uncompressed_stream_size:
      size = self._uncompressed_stream_size - self._current_offset

    if self._realign_offset:
      self._AlignUncompressedDataOffset(self._current_offset)
      self._realign_offset = False

    uncompressed_data = ''

    while self._uncompressed_data_offset + size > self._uncompressed_data_size:
      uncompressed_data = ''.join([
          uncompressed_data,
          self._uncompressed_data[self._uncompressed_data_offset]])

      remaining_uncompressed_data_size = (
          self._uncompressed_data_size - self._uncompressed_data_offset)

      self._current_offset += remaining_uncompressed_data_size
      size -= remaining_uncompressed_data_size

      _ = self._ReadCompressedData(self._COMPRESSED_DATA_BUFFER_SIZE)

      self._uncompressed_data_offset = 0

    if (self > 0 and
        self._uncompressed_data_offset + size <= self._uncompressed_data_size):
      slice_start_offset = self._uncompressed_data_offset
      slice_end_offset = slice_start_offset + size

      uncompressed_data = ''.join([
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
              or relative position within the file. Default is SEEK_SET.

    Raises:
      IOError: if the seek failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if self._current_offset < 0:
      raise IOError(
          u'Invalid current offset: {0:d} value less than zero.'.format(
              self._current_offset))

    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self._uncompressed_data_size
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

    if self._uncompressed_stream_size is None:
      self._uncompressed_stream_size = self._GetUncompressedStreamSize()

    return self._uncompressed_stream_size
