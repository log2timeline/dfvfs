#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The dfVFS Project Authors.
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
"""The operating system file-like object implementation."""

import os

from dfvfs.file_io import file_io
from dfvfs.lib import errors


class OSFile(file_io.FileIO):
  """Class that implements a file-like object using os."""

  def __init__(self, resolver_context):
    """Initializes the file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
    """
    super(OSFile, self).__init__(resolver_context)
    self._file_object = None
    self._size = 0

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.

  def open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: optional path specification (instance of path.PathSpec).
                 The default is None.
      mode: optional file access mode. The default is 'rb' read-only binary.

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

    if path_spec.HasParent():
      raise errors.PathSpecError(u'Unsupported path specification with parent.')

    location = getattr(path_spec, 'location', None)

    if location is None:
      raise errors.PathSpecError(u'Path specification missing location.')

    self._file_object = open(location, mode=mode)

    stat_info = os.stat(location)
    self._size = stat_info.st_size

  def close(self):
    """Closes the file-like object.

    Raises:
      IOError: if the close failed.
    """
    if not self._file_object:
      raise IOError(u'Not opened.')

    self._resolver_context.RemoveFileObject(self)
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
    if not self._file_object:
      raise IOError(u'Not opened.')

    if size is None:
      size = self._size - self._file_object.tell()

    return self._file_object.read(size)

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks an offset within the file-like object.

    Args:
      offset: The offset to seek.
      whence: Optional value that indicates whether offset is an absolute
              or relative position within the file. Default is SEEK_SET.

    Raises:
      IOError: if the seek failed.
    """
    if not self._file_object:
      raise IOError(u'Not opened.')

    # For a yet unknown reason a Python file-like object on Windows allows for
    # invalid whence values to be passed to the seek function. This check
    # makes sure the behavior of the function is the same on all platforms.
    if whence not in [os.SEEK_SET, os.SEEK_CUR, os.SEEK_END]:
      raise IOError(u'Invalid whence value.')

    return self._file_object.seek(offset, whence)

  def get_offset(self):
    """Returns the current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._file_object:
      raise IOError(u'Not opened.')

    return self._file_object.tell()

  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._file_object:
      raise IOError(u'Not opened.')

    return self._size
