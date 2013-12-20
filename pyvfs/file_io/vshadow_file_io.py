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
"""The Volume Shadow Snapshots (VSS) file-like object implementation."""

import os

# This is necessary to prevent a circular import.
import pyvfs.vfs.manager

from pyvfs.file_io import file_io
from pyvfs.lib import errors


class VShadowFile(file_io.FileIO):
  """Class that implements a file-like object using pyvshadow."""

  def __init__(self, vshadow_volume=None, vshadow_store=None):
    """Initializes the file-like object.

    Args:
      vshadow_volume: optional VSS volume object (instance of
                      pyvshadow.volume). The default is None.
      vshadow_store: optional VSS store object (instance of pyvshadow.store).
                     The default is None.

    Raises:
      ValueError: if vshadow_store provided but vshadow_volume is not.
    """
    if vshadow_store is not None and vshadow_volume is None:
      raise ValueError(
          u'VShadow store object provided without corresponding volume object.')

    super(VShadowFile, self).__init__()
    self._vshadow_volume = vshadow_volume
    self._vshadow_store = vshadow_store

    if vshadow_store:
      self._vshadow_store_set_in_init = True
    else:
      self._vshadow_store_set_in_init = False
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

    if not self._vshadow_store_set_in_init:
      file_system = pyvfs.vfs.manager.FileSystemManager.OpenFileSystem(
          path_spec)
      self._vshadow_volume = file_system.GetVShadowVolume()

      store_index = getattr(path_spec, 'store_index', None)

      if store_index is None:
        raise errors.PathSpecError(
            u'Path specification missing store index.')

      self._vshadow_store = self._vshadow_volume.get_store(store_index)

    self._is_open = True

  def close(self):
    """Closes the file-like object.

    Raises:
      IOError: if the close failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if not self._vshadow_store_set_in_init:
      self._vshadow_store = None

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

    return self._vshadow_store.read(size)

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

    self._vshadow_store.seek(offset, whence)

  def get_offset(self):
    """Returns the current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._vshadow_store.get_offset()

  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._vshadow_store.volume_size
