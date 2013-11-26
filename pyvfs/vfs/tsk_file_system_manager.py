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
"""The SleuthKit file system manager object."""

# This is necessary to prevent a circular import.
import pyvfs.vfs.tsk_file_system

from pyvfs.resolver import resolver


class TSKFileSystemManager(object):
  """Class that implements the SleuthKit file system manager."""

  _file_system_objects = {}

  @classmethod
  def OpenPathSpec(cls, path_spec):
    """Opens a file system object defined by path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).

    Returns:
      The file-like object (instance of vfs.FileSystem) or None if the path
      specification could not be resolved.
    """
    if path_spec not in cls._file_system_objects:
      # TODO: remove debug statement after validating if this works.
      print "TSKFileSystemManager.OpenPathSpec cache miss"

      file_object = resolver.Resolver.OpenPathSpec(path_spec)

      if file_object is None:
        return

      file_system = pyvfs.vfs.tsk_file_system.TSKFileSystem(file_object)
      cls._file_system_objects[path_spec] = file_system

    else:
      # TODO: remove debug statement after validating if this works.
      print "TSKFileSystemManager.OpenPathSpec cache hit"

      file_system = cls._file_system_objects[path_spec]

    return file_system.GetFsInfo()
