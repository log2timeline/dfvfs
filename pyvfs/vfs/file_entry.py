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
"""The Virtual File System (VFS) file entry object interface.

The file entry can be various file system elments like a regular file,
a directory or file system metadata.
"""

import abc


class FileEntry(object):
  """The VFS file entry object interface."""

  def __init__(self, file_system, path_spec):
    """Initializes the file entry object.

    Args:
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification object (instance of path.PathSpec).
    """
    super(FileEntry, self).__init__()
    self.file_system = file_system
    self.path_spec = path_spec

  @abc.abstractmethod
  def GetData(self):
    """Retrieves the file-like object (instance of io.FileIO) of the data."""

  @abc.abstractmethod
  def GetStat(self):
    """Retrieves the stat object (instance of vfs.Stat)."""
