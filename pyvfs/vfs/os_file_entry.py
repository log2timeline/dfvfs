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
import stat

from pyvfs.file_io import os_file_io
from pyvfs.path import os_path_spec
from pyvfs.vfs import file_entry
from pyvfs.vfs import vfs_stat


class OSDirectory(file_entry.Directory):
  """Class that implements a directory object using os."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

       Since a directory can contain a vast number of entries using
       a generator is more memory efficient.

    Yields:
      A path specification (instance of path.OSPathSpec).
    """
    location = getattr(self.path_spec, 'location', None)

    if location is None:
      return

    for directory_entry in os.listdir(location):
      yield os_path_spec.OSPathSpec(
          location=os.path.join(location, directory_entry))


class OSFileEntry(file_entry.FileEntry):
  """Class that implements a file entry object using os."""

  def __init__(self, file_system, path_spec):
    """Initializes the file entry object.

    Args:
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification object (instance of path.PathSpec).
    """
    super(OSFileEntry, self).__init__(file_system, path_spec)
    self._directory = None
    self._file_object = None
    self._stat_object = None

  def _GetDirectory(self):
    """Retrieves the directory object (instance of OSDirectory)."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if (self._stat_object and
        self._stat_object.type == self._stat_object.TYPE_DIRECTORY):
      return OSDirectory(self.path_spec)
    return

  def _GetStat(self):
    """Retrieves the stat object (instance of vfs.VFSStat)."""
    location = getattr(self.path_spec, 'location', None)

    if location is None:
      return

    stat_info = os.stat(location)
    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    stat_object.size = stat_info.st_size

    # Date and time stat information.
    stat_object.atime = stat_info.st_atime
    stat_object.ctime = stat_info.st_ctime
    stat_object.mtime = stat_info.st_mtime

    # Ownership and permissions stat information.
    stat_object.mode = stat.S_IMODE(stat_info.st_mode)
    stat_object.uid = stat_info.st_uid
    stat_object.gid = stat_info.st_gid

    # File entry type stat information.
    if stat.S_ISREG(stat_info.st_mode):
      stat_object.type = stat_object.TYPE_FILE
    elif stat.S_ISDIR(stat_info.st_mode):
      stat_object.type = stat_object.TYPE_DIRECTORY
    elif stat.S_ISLNK(stat_info.st_mode):
      stat_object.type = stat_object.TYPE_LINK
    elif (stat.S_ISCHR(stat_info.st_mode) or
          stat.S_ISBLK(stat_info.st_mode)):
      stat_object.type = stat_object.TYPE_DEVICE
    elif stat.S_ISFIFO(stat_info.st_mode):
      stat_object.type = stat_object.TYPE_PIPE
    elif stat.S_ISSOCK(stat_info.st_mode):
      stat_object.type = stat_object.TYPE_SOCKET

    # Other stat information.
    # stat_object.ino = stat_info.st_ino
    # stat_object.dev = stat_info.st_dev
    # stat_object.nlink = stat_info.st_nlink
    # stat_object.fs_type = 'Unknown'
    stat_object.allocated = True

    return stat_object

  @property
  def name(self):
    """The name of the file entry, which does not include the full path."""
    location = getattr(self.path_spec, 'location', '')
    return os.path.basename(location)

  @property
  def sub_file_entries(self):
    """The sub file entries (list of instance of vfs.FileEntry)."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    sub_file_entries = []
    if self._directory:
      for path_spec in self._directory.entries:
        sub_file_entries.append(
            OSFileEntry(self._file_system, path_spec))
    return sub_file_entries

  def GetFileObject(self):
    """Retrieves the file-like object (instance of file_io.FileIO)."""
    if not self._file_object:
      self._file_object = os_file_io.OSFile()
      self._file_object.open(self.path_spec)
    return self._file_object

  def GetStat(self):
    """Retrieves the stat object (instance of vfs.Stat)."""
    if self._stat_object is None:
      self.GetStat()
    return self._stat_object
