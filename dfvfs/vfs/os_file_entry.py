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
"""The operating system file entry implementation."""

import os
import stat

from dfvfs.lib import definitions
from dfvfs.file_io import os_file_io
from dfvfs.path import os_path_spec
from dfvfs.vfs import file_entry
from dfvfs.vfs import vfs_stat


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

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_OS

  def __init__(self, file_system, path_spec, is_root=False):
    """Initializes the file entry object.

    Args:
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification object (instance of path.PathSpec).
      is_root: optional boolean value to indicate if the file entry is
               the root file entry of the corresponding file system.
               The default is False.
    """
    super(OSFileEntry, self).__init__(
        file_system, path_spec, is_root=is_root, is_virtual=False)
    self._name = None

  def _GetDirectory(self):
    """Retrieves the directory object (instance of OSDirectory)."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if (self._stat_object and
        self._stat_object.type == self._stat_object.TYPE_DIRECTORY):
      return OSDirectory(self._file_system, self.path_spec)
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
    stat_object.ino = stat_info.st_ino
    # stat_info.st_dev
    # stat_info.st_nlink

    return stat_object

  @property
  def name(self):
    """The name of the file entry, which does not include the full path."""
    if self._name is None:
      location = getattr(self.path_spec, 'location', None)
      if location is not None:
        self._name = self._file_system.BasenamePath(location)
    return self._name

  @property
  def sub_file_entries(self):
    """The sub file entries (generator of instance of vfs.FileEntry)."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield OSFileEntry(self._file_system, path_spec)

  def GetFileObject(self):
    """Retrieves the file-like object (instance of file_io.FileIO)."""
    file_object = os_file_io.OSFile()
    file_object.open(self.path_spec)
    return file_object

  def GetParentFileEntry(self):
    """Retrieves the parent file entry."""
    location = getattr(self.path_spec, 'location', None)
    if location is None:
      return
    parent_location = self._file_system.DirnamePath(location)
    if parent_location is None:
      return
    if parent_location == u'':
      parent_location = self._file_system.PATH_SEPARATOR

    path_spec = os_path_spec.OSPathSpec(location=parent_location)
    return OSFileEntry(self._file_system, path_spec)
