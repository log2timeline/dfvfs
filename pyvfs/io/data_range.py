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
"""File-like object that maps a specific data range within a file."""

import os

from pyvfs.io import file_io


class DataRange(file_io.FileIO):
  """File-like object that maps a specific data range within a file.

     The data range object allows to expose a single partition within
     a full disk image as a separate file-like object by mapping
     the data range (offset and size) fo the volume on top of the full disk
     image.
  """
  def __init__(self, file_object=None):
    """Initialize the data range file-like object.

       If the file-like object is chained do not separately use the parent
       file-like object.

    Args:
      file_object: The chained file-like object can be None if open is used.
                   Default is None.
    """
    super(DataRange, self).__init__()
    self._file_object = file_object
    self._current_offset = 0
    self._range_offset = -1
    self._range_size = -1

    if file_object:
      self._file_object_set_in_init = True
    else:
      self._file_object_set_in_init = False

  def SetRange(self, range_offset, range_size):
    """Sets the data range (offset and size).

    The data range is used to map a range of data within one file
    (e.g. a single partition within a full disk image) as a file-like object.

    Args:
      range_offset: The start offset of the data range.
      range_size: The size of the data range.

    Raises:
      ValueError: if either the range offset or size is invalid.
    """
    if range_offset < 0:
      raise ValueError(
          'Invalid range offset: {0:d} value out of bounds.'.format(
              range_offset))

    if range_size < 0:
      raise ValueError(
          'Invalid range size: {0:d} value out of bounds.'.format(
              range_size))

    self._range_offset = range_offset
    self._range_size = range_size
    self._current_offset = 0

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.

  def open(self, path_spec, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: The VFS path specification (instance of PathSpec).

    Raises:
      IOError: if the open file-like object could not be opened.
    """
    if not self._file_object_set_in_init:
      if self._file_object:
        # TODO: add more info to the error string.
        raise IOError('Already open.')

      # TODO: add VFS support.
      # TODO: set range based on VFS.
      self._file_object = open(path_spec, mode)

  def close(self):
    """Closes the file-like object.

       If the file-like object was passed in the init function
       the data range object does not control the file-like object
       and should not actually close the file-like object.

    Raises:
      IOError: if the close failed.
    """
    if not self._file_object_set_in_init:
      if not self._file_object:
        raise IOError('Already closed.')
      self._file_object.close()
      self._file_object = None

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
    if self._range_offset < 0 or self._range_size < 0:
      raise IOError('Invalid data range.')

    if self._current_offset < 0:
      raise IOError(
          'Invalid current offset: {0:d} value less than zero.'.format(
              self._current_offset))

    if self._current_offset >= self._range_size:
      return ''

    if size is None:
      size = self._range_size
    if self._current_offset + size > self._range_size:
      size = self._range_size - self._current_offset

    self._file_object.seek(
        self._range_offset + self._current_offset, os.SEEK_SET)

    data = self._file_object.read(size)

    self._current_offset += len(data)

    return data

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks an offset within the file-like object.

    Args:
      offset: The offset to seek.
      whence: Optional value that indicates whether offset is an absolute
              or relative position within the file. Default is SEEK_SET.

    Raises:
      IOError: if the seek failed.
    """
    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self.self_range_size
    elif whence != os.SEEK_SET:
      raise IOError('Unsupported whence.')
    if offset < 0:
      raise IOError('Invalid offset value less than zero.')
    self._current_offset = offset

  def get_offset(self):
    """Returns the current offset into the file-like object."""
    return self._current_offset

  def get_size(self):
    """Returns the size of the file-like object."""
    return self._range_size
