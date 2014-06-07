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
"""The gzip file system implementation."""

from dfvfs.lib import definitions
from dfvfs.path import gzip_path_spec
from dfvfs.vfs import gzip_file_entry
from dfvfs.vfs import root_only_file_system


class GzipFileSystem(root_only_file_system.RootOnlyFileSystem):
  """Class that implements a file system object using gzip."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_GZIP

  def __init__(self, resolver_context, path_spec):
    """Initializes the file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      path_spec: the path specification (instance of path.PathSpec) of
                 the file-like object.
    """
    super(GzipFileSystem, self).__init__(resolver_context)
    self._path_spec = path_spec

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    path_spec = gzip_path_spec.GzipPathSpec(parent=self._path_spec)
    return gzip_file_entry.GzipFileEntry(
        self._resolver_context, self, path_spec, is_root=True, is_virtual=True)
