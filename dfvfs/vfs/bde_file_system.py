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
"""The BDE file system implementation."""

from dfvfs.lib import definitions
from dfvfs.path import bde_path_spec
from dfvfs.vfs import bde_file_entry
from dfvfs.vfs import root_only_file_system


class BdeFileSystem(root_only_file_system.RootOnlyFileSystem):
  """Class that implements a file system object using BDE."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BDE

  def __init__(self, resolver_context, bde_volume, path_spec):
    """Initializes the file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      bde_volume: the BDE volume object (instance of pybde.volume).
      path_spec: the path specification (instance of path.PathSpec) of
                 the file-like object.
    """
    super(BdeFileSystem, self).__init__(resolver_context)
    self._bde_volume = bde_volume
    self._path_spec = path_spec

  def GetBdeVolume(self):
    """Retrieves the BDE volume object.

    Returns:
      The BDE volume object (instance of pybde.volume).
    """
    return self._bde_volume

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    path_spec = bde_path_spec.BdePathSpec(parent=self._path_spec)
    return bde_file_entry.BdeFileEntry(
        self._resolver_context, self, path_spec, is_root=True, is_virtual=True)
