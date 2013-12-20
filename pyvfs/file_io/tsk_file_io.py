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
"""The SleuthKit (TSK) file-like object implementation."""

import os
import pytsk3

# This is necessary to prevent a circular import.
import pyvfs.vfs.manager

from pyvfs.file_io import file_io
from pyvfs.lib import errors


class TSKFile(file_io.FileIO):
  """Class that implements a file-like object using pytsk3."""

  def __init__(self, tsk_file_system=None, tsk_file=None):
    """Initializes the file-like object.

    Args:
      tsk_file_system: optional SleuthKit file system object (instance of
                       pytsk3.FS_Info). The default is None.
      tsk_file: optional SleuthKit file object (instance of pytsk3.File).
                The default is None.

    Raises:
      ValueError: if tsk_file provided but tsk_file_system is not.
    """
    if tsk_file is not None and tsk_file_system is None:
      raise ValueError(
          u'TSK file object provided without corresponding file system '
          u'object.')

    super(TSKFile, self).__init__()
    self._tsk_file_system = tsk_file_system
    self._tsk_file = tsk_file
    self._current_offset = 0
    self._size = 0

    if tsk_file:
      self._tsk_file_set_in_init = True
    else:
      self._tsk_file_set_in_init = False
    self._is_open = False

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.

  def open(self, path_spec, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).
      mode: the file access mode, the default is 'rb' read-only binary.

    Raises:
      IOError: if the open file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification or mode is invalid.
    """
    if not path_spec:
      raise ValueError(u'Missing path specfication.')

    if mode != 'rb':
      raise ValueError(u'Unsupport mode: {0:s}.'.format(mode))

    if self._is_open:
      raise IOError(u'Already open.')

    if not self._tsk_file_set_in_init:
      file_system = pyvfs.vfs.manager.FileSystemManager.OpenFileSystem(
          path_spec)
      self._tsk_file_system = file_system.GetFsInfo()

      # Opening a file by inode number is faster than opening a file
      # by location.
      inode = getattr(path_spec, 'inode', None)
      location = getattr(path_spec, 'location', None)

      if inode is not None:
        self._tsk_file = self._tsk_file_system.open_meta(inode=inode)
      elif location is not None:
        self._tsk_file = self._tsk_file_system.open(location)
      else:
        raise errors.PathSpecError(
            u'Path specification missing inode and location.')

      # Note that because pytsk3.File does not explicitly defines info
      # we need to check if the attribute exists and has a value other
      # than None.
      if getattr(self._tsk_file, 'info', None) is None:
        raise IOError(u'Missing attribute info in file (pytsk3.File).')

      # Note that because pytsk3.TSK_FS_FILE does not explicitly defines meta
      # we need to check if the attribute exists and has a value other
      # than None.
      if getattr(self._tsk_file.info, 'meta', None) is None:
        raise IOError(
            u'Missing attribute meta in file.info pytsk3.TSK_FS_FILE).')

      # Note that because pytsk3.TSK_FS_META does not explicitly defines size
      # we need to check if the attribute exists.
      if not hasattr(self._tsk_file.info.meta, 'size'):
        raise IOError(
            u'Missing attribute size in file.info.meta (pytsk3.TSK_FS_META).')

      # Note that because pytsk3.TSK_FS_META does not explicitly defines type
      # we need to check if the attribute exists.
      if not hasattr(self._tsk_file.info.meta, 'type'):
        raise IOError(
            u'Missing attribute type in file.info.meta (pytsk3.TSK_FS_META).')

      if self._tsk_file.info.meta.type != pytsk3.TSK_FS_META_TYPE_REG:
        raise IOError(u'Not a regular file.')

    self._current_offset = 0
    self._size = self._tsk_file.info.meta.size
    self._is_open = True

  def close(self):
    """Closes the file-like object.

    Raises:
      IOError: if the close failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if not self._tsk_file_set_in_init:
      self._tsk_file = None

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
      raise IOError(u'Invalid current offset value less than zero.')

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
    if not self._is_open:
      raise IOError(u'Not opened.')

    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self._size
    elif whence != os.SEEK_SET:
      raise IOError(u'Unsupported whence.')

    if offset < 0:
      raise IOError(u'Invalid offset value less than zero.')

    self._current_offset = offset

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

    return self._size
