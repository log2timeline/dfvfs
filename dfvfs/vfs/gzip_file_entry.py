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
"""The gzip file entry implementation."""

# This is necessary to prevent a circular import.
import dfvfs.file_io.gzip_file_io

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.vfs import root_only_file_entry
from dfvfs.vfs import vfs_stat


class GzipFileEntry(root_only_file_entry.RootOnlyFileEntry):
  """Class that implements a file entry object using gzip."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_GZIP

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False):
    """Initializes the file entry object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification object (instance of path.PathSpec).
      is_root: optional boolean value to indicate if the file entry is
               the root file entry of the corresponding file system.
               The default is False.
      is_virtual: optional boolean value to indicate if the file entry is
                  a virtual file entry emulated by the corresponding file
                  system. The default is False.
    """
    super(GzipFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._gzip_file = None

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of vfs.VFSStat).

    Raises:
      BackEndError: when the gzip file is missing.
    """
    if self._gzip_file is None:
      self._gzip_file = self.GetGzipFile()

    if self._gzip_file is None:
      raise errors.BackEndError(u'Missing gzip file.')

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    stat_object.size = self._gzip_file.uncompressed_data_size

    # Date and time stat information.
    stat_object.mtime = self._gzip_file.modification_time

    # Ownership and permissions stat information.

    # File entry type stat information.
    stat_object.type = stat_object.TYPE_FILE

    # Other stat information.
    # gzip_file.comment
    # gzip_file.operating_system
    # gzip_file.original_filename

    return stat_object

  def GetFileObject(self):
    """Retrieves the file-like object (instance of file_io.FileIO)."""
    file_object = dfvfs.file_io.gzip_file_io.GzipFile(self._resolver_context)
    file_object.open(path_spec=self.path_spec)
    return file_object

  def GetGzipFile(self):
    """Retrieves the gzip file object.

    Returns:
      The gzip file object (instance of file_io.GzipFile).
    """
    gzip_file = dfvfs.file_io.gzip_file_io.GzipFile(self._resolver_context)
    gzip_file.open(path_spec=self.path_spec)
    return gzip_file
