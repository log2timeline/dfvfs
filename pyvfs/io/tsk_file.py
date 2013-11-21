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
"""Read-only file-like object implementation using the SleuthKit (TSK)."""

import os
import pytsk3

from pyvfs.io import file_io


class TSKFile(file_io.FileIO):
  """Class that implements a read-only file-like object using SleuthKit."""

  def __init__(self, tsk_file_system):
    """Initializes the SleuthKit file-like object.

    Args:
      tsk_file_system: A SleuthKit file system (pytsk3.FS_Info) object.
    """
    super(TSKFile, self).__init__()
    self._tsk_file_system = tsk_file_system
    self._tsk_file = None
    self._current_offset = 0

  def open(self, path_spec, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: The VFS path specification (instance of PathSpec).

    Raises:
      IOError: if the open file-like object could not be opened.
      ValueError: if the path specification is incorrect.
    """
    # Opening a file by inode number is faster than opening a file by location.
    inode = getattr(path_spec, 'inode', None)
    location = getattr(path_spec, 'location', None)

    if inode is not None:
      self._tsk_file = self._tsk_file_system.open_meta(inode=inode)
    elif location is not None:
      self._tsk_file = self._tsk_file_system.open(location)
    else:
      raise ValueError('Path specification missing inode and location.')

    if not self._tsk_file.info.meta:
      raise IOError('Missing file metadata.')

    if self._tsk_file.info.meta.type != pytsk3.TSK_FS_META_TYPE_REG:
      raise IOError('Not a regular file.')

    self._current_offset = 0
    self._size = self._tsk_file.info.meta.size

  def close(self):
    """Closes the file-like object."""
    self._tsk_file = None

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
    if self._current_offset < 0:
      raise IOError('Invalid current offset value less than zero.')

    if self._current_offset > self._size:
      return ''

    if size is None or self._current_offset + size > self._size:
      size = self._size - self._current_offset

    data = self._tsk_file.read_random(self._current_offset, size)

    # It is possible the that returned data size is not the same as the
    # requested data size. At this layer we don't care and this discrepancy
    # should be dealt with on a higher layer if necessary.
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
      offset += self._size
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
    return self._size
