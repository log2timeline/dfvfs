#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 The dfVFS Project Authors.
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
"""The fake file system implementation."""

from dfvfs.lib import date_time
from dfvfs.lib import definitions
from dfvfs.path import fake_path_spec
from dfvfs.vfs import file_system
from dfvfs.vfs import fake_file_entry
from dfvfs.vfs import vfs_stat


class FakeFileSystem(file_system.FileSystem):
  """Class that implements a fake file system object."""

  _LOCATION_ROOT = u'/'

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FAKE

  def __init__(self, resolver_context):
    """Initializes the file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
    """
    super(FakeFileSystem, self).__init__(resolver_context)
    self._paths = {}

  def AddFileEntry(
      self, path, file_entry_type=definitions.FILE_ENTRY_TYPE_FILE,
      file_data=None):
    """Adds a fake file entry.

    Args:
      path: the path of the file entry.
      file_entry_type: optional type of the file entry object.
                       The default is file (definitions.FILE_ENTRY_TYPE_FILE).
      file_data: optional data of the fake file-like object.
                 The default is None.

    Raises:
      KeyError: if the path already exists.
    """
    if path in self._paths:
      raise KeyError(u'File entry already set for path: {0:s}.'.format(path))

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    if file_data is not None:
      stat_object.size = len(file_data)

    # Date and time stat information.
    timestamp = date_time.PosixTimestamp.GetNow()

    stat_object.atime = timestamp
    stat_object.ctime = timestamp
    stat_object.mtime = timestamp

    # Ownership and permissions stat information.

    # File entry type stat information.
    stat_object.type = file_entry_type

    # Other stat information.

    self._paths[path] = (stat_object, file_data)

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      Boolean indicating if the file entry exists.
    """
    location = getattr(path_spec, 'location', None)

    if location is None or location not in self._paths:
      return False
    return True

  def GetFileDataByPath(self, path):
    """Retrieves the file data for a path.

    Args:
      path: a path.

    Returns:
      Binary string containing the file data or None if not available.
    """
    _, file_data = self._paths.get(path, (None, None))
    return file_data

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    if not self.FileEntryExistsByPathSpec(path_spec):
      return
    return fake_file_entry.FakeFileEntry(
        self._resolver_context, self, path_spec)

  def GetPaths(self):
    """Retrieves the paths dictionary.

    Returns:
      Dictionary containing the paths and the file-like objects.
    """
    return self._paths

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    path_spec = fake_path_spec.FakePathSpec(location=self._LOCATION_ROOT)
    return fake_file_entry.FakeFileEntry(
        self._resolver_context, self, path_spec, is_root=True)

  def GetStatObjectByPath(self, path):
    """Retrieves the stat object for a path.

    Args:
      path: a path.

    Returns:
      The stat object (instance of vfs_stat.VFSStat).
    """
    stat_object, _ = self._paths.get(path, (None, None))
    return stat_object
