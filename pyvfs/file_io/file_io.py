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
"""The Virtual File System (VFS) file-like object interface."""

import abc
import os


# Since this class implements the file-like object interface
# the names of the interface functions are in lower case as an exception
# to the normal naming convention.


class FileIO(object):
  """Class that implements the VFS file-like object interface."""

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.

  @abc.abstractmethod
  def open(self, path_spec, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).
      mode: the file access mode, the default is 'rb' read-only binary.

    Raises:
      IOError: if the open file-like object could not be opened.
    """

  @abc.abstractmethod
  def close(self):
    """Closes the file-like object.

    Raises:
      IOError: if the close failed.
    """

  @abc.abstractmethod
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

  @abc.abstractmethod
  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks an offset within the file-like object.

    Args:
      offset: The offset to seek.
      whence: Optional value that indicates whether offset is an absolute
              or relative position within the file. Default is SEEK_SET.

    Raises:
      IOError: if the seek failed.
    """

  # get_offset() is preferred above tell() by the libbfio layer used in libyal.
  @abc.abstractmethod
  def get_offset(self):
    """Returns the current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """

  # Pythonesque alias for get_offset().
  def tell(self):
    """Returns the current offset into the file-like object."""
    return self.get_offset()

  @abc.abstractmethod
  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
