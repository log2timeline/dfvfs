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
"""The operating system file entry implementation."""

import os

from pyvfs.vfs import file_entry
from pyvfs.vfs import stat


class OSFileEntry(file_entry.FileEntry):
  """The operating system file entry implementation."""

  def __init__(self, path_spec, file_system):
    """Initializes the file entry object.

    Args:
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification object (instance of path.PathSpec).
    """
    super(OSFileEntry, self).__init__(file_system, path_spec)
    self._stat_object = None

  def GetData(self):
    """Retrieves the file-like object (instance of io.FileIO) of the data."""
    # TODO: implement.
    pass

  def GetStat(self):
    """Retrieves the stat object (instance of vfs.Stat)."""
    # TODO validate path spec.
    location = getattr(self.path_spec, 'location', None)

    if location is None:
      return None

    if self._stat_object is None:
      stat_info = os.stat(self.path_spec.name)
      self._stat_object = stat.Stat()

      # File data stat information.
      self._stat_object.size = stat_info.st_size

      # Date and time stat information.
      self._stat_object.atime = stat_info.st_atime
      self._stat_object.ctime = stat_info.st_ctime
      self._stat_object.mtime = stat_info.st_mtime

      # Ownership and permissions stat information.
      self._stat_object.uid = stat_info.st_uid
      self._stat_object.gid = stat_info.st_gid

      # Other stat information.
      self._stat_object.mode = stat_info.st_mode
      self._stat_object.ino = stat_info.st_ino
      self._stat_object.dev = stat_info.st_dev
      self._stat_object.nlink = stat_info.st_nlink
      self._stat_object.fs_type = 'Unknown'
      self._stat_object.allocated = True

    return self._stat_object
