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
"""The SleuthKit (TSK) file system implementation."""

import pytsk3

# This is necessary to prevent a circular import.
import pyvfs.vfs.tsk_file_entry

from pyvfs.lib import definitions
from pyvfs.lib import tsk_image
from pyvfs.path import tsk_path_spec
from pyvfs.vfs import file_system


class TSKFileSystem(file_system.FileSystem):
  """Class that implements a file system object using pytsk3."""

  _LOCATION_ROOT = u'/'

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK

  def __init__(self, file_object, path_spec, offset=0):
    """Initializes the file system object.

    Args:
      file_object: the file-like object (instance of file_io.FileIO).
      path_spec: the path specification (instance of path.PathSpec) of
                 the file-like object.
      offset: option offset, in bytes, of the start of the file system,
              the default is 0.
    """
    super(TSKFileSystem, self).__init__()
    self._file_object = file_object
    self._path_spec = path_spec

    tsk_image_object = tsk_image.TSKFileSystemImage(file_object)
    self._tsk_file_system = pytsk3.FS_Info(tsk_image_object, offset=offset)

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      Boolean indicating if the file entry exists.
    """
    tsk_file = None
    inode = getattr(path_spec, 'inode', None)
    location = getattr(path_spec, 'location', None)

    try:
      if inode is not None:
        tsk_file = self._tsk_file_system.open_meta(inode=inode)
      elif location is not None:
        tsk_file = self._tsk_file_system.open(location)

    except IOError:
      pass

    return tsk_file is not None

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    # Opening a file by inode number is faster than opening a file by location.
    tsk_file = None
    inode = getattr(path_spec, 'inode', None)
    location = getattr(path_spec, 'location', None)

    try:
      if inode is not None:
        tsk_file = self._tsk_file_system.open_meta(inode=inode)
      elif location is not None:
        tsk_file = self._tsk_file_system.open(location)

    except IOError:
      pass

    if tsk_file is None:
      return
    # TODO: is there a way to determine the parent inode number here?
    return pyvfs.vfs.tsk_file_entry.TSKFileEntry(
        self, path_spec, tsk_file=tsk_file)

  def GetFsInfo(self):
    """Retrieves the file system info object.

    Returns:
      The SleuthKit file system info object (instance of
      pytsk3.FS_Info).
    """
    return self._tsk_file_system

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry).
    """
    tsk_file = self._tsk_file_system.open(self._LOCATION_ROOT)

    path_spec = tsk_path_spec.TSKPathSpec(
        location=self._LOCATION_ROOT, parent=self._path_spec)

    # TODO: is there a way to determine the parent inode number here?
    return pyvfs.vfs.tsk_file_entry.TSKFileEntry(
        self, path_spec, tsk_file=tsk_file)
