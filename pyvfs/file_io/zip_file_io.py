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
"""The zip extracted file-like object implementation."""

# Note: that zipfile.ZipExtFile is not seekable, hence it is wrapped in
# an instance of file_io.FileIO.

import os

# This is necessary to prevent a circular import.
import pyvfs.vfs.manager

from pyvfs.file_io import file_io


class ZipFile(file_io.FileIO):
  """Class that implements a file-like object using zipfile."""

  # The size of the uncompressed data buffer.
  _UNCOMPRESSED_DATA_BUFFER_SIZE = 16 * 1024 * 1024

  def __init__(self, zip_info=None, zip_file=None):
    """Initializes the file-like object.

    Args:
      zip_info: optional zip info object (instance of zipfile.ZipInfo).
                The default is None.
      zip_file: optional extracted file-like object (instance of
                zipfile.ZipFile). The default is None.

    Raises:
      ValueError: if zip_file provided but zip_info is not.
    """
    if zip_file is not None and zip_info is None:
      raise ValueError(
          u'Zip extracted file object provided without corresponding info '
          u'object.')

    super(ZipFile, self).__init__()
    self._zip_info = zip_info
    self._zip_file = zip_file
    self._compressed_data = ''
    self._current_offset = 0
    self._realign_offset = True
    self._uncompressed_data = ''
    self._uncompressed_data_offset = 0
    self._uncompressed_data_size = 0
    self._uncompressed_stream_size = None
    self._zip_ext_file = None

    if zip_file:
      self._zip_file_set_in_init = True
    else:
      self._zip_file_set_in_init = False
    self._is_open = False

  def _AlignUncompressedDataOffset(self, uncompressed_data_offset):
    """Aligns the compressed file with the uncompressed data offset.

    Args:
      uncompressed_data_offset: the uncompressed data offset.
    """
    if self._zip_ext_file:
      self._zip_ext_file.close()
      self._zip_ext_file = None

    self._zip_ext_file = self._zip_file.open(self._zip_info, 'r')

    self._uncompressed_data = ''

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

  def open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: optional the path specification (instance of path.PathSpec).
                 The default is None.
      mode: the file access mode, the default is 'rb' read-only binary.

    Raises:
      IOError: if the open file-like object could not be opened.
      ValueError: if the path specification or mode is invalid.
    """
    if not self._zip_file_set_in_init and not path_spec:
      raise ValueError(u'Missing path specfication.')

    if mode != 'rb':
      raise ValueError(u'Unsupport mode: {0:s}.'.format(mode))

    if self._is_open:
      raise IOError(u'Already open.')

    if not self._zip_file_set_in_init:
      file_system = pyvfs.vfs.manager.FileSystemManager.OpenFileSystem(
          path_spec)

      file_entry = file_system.GetFileEntryByPathSpec(path_spec)

      self._zip_info = file_entry.GetZipInfo()
      self._zip_file = file_entry.GetZipFile()

    self._current_offset = 0
    self._uncompressed_stream_size = self._zip_info.file_size
    self._is_open = True

  def close(self):
    """Closes the file-like object.

       If the file-like object was passed in the init function
       the data range file-like object does not control the file-like object
       and should not actually close it.

    Raises:
      IOError: if the close failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if not self._zip_file_set_in_init:
      if self._zip_ext_file:
        self._zip_ext_file.close()
        self._zip_ext_file = None

      self._zip_file = None
      self._zip_info = None

    self._is_open = False

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
      return ''

    if (size is None or
        self._current_offset + size > self._uncompressed_stream_size):
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

      self._ReadCompressedData(self._UNCOMPRESSED_DATA_BUFFER_SIZE)

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
