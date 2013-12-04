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
"""The file system manager object."""

from pyvfs.resolver import resolver


class FileSystemManager(object):
  """Class that implements the file system manager."""

  _file_system_objects = {}

  @classmethod
  def OpenFileSystem(cls, path_spec):
    """Opens a file system object defined by path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).

    Returns:
      The file system object (instance of vfs.FileSystem) or None if the path
      specification could not be resolved.
    """
    if path_spec not in cls._file_system_objects:
      file_system = resolver.Resolver.OpenFileSystem(path_spec)
      cls._file_system_objects[path_spec] = file_system

    return cls._file_system_objects[path_spec]

  # TODO: make sure non-used cached file systems are released.
