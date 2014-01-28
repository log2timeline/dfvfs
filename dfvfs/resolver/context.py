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
"""The resolver context object."""

from dfvfs.resolver import cache


class Context(object):
  """Class that implements the resolver context."""

  def __init__(
      self, maximum_number_of_file_objects=128,
      maximum_number_of_file_systems=16):
    """Initializes the resolver context object.

    Args:
      maximum_number_of_file_objects: optional maximum number of file-like
                                      objects cached in the context. The
                                      default is 128.
      maximum_number_of_file_systems: optional maximum number of file system
                                      objects cached in the context. The
                                      default is 16.
    """
    super(Context, self).__init__()
    self._file_object_cache = cache.ObjectsCache(
        maximum_number_of_file_objects)
    self._file_system_cache = cache.ObjectsCache(
        maximum_number_of_file_systems)

  def CacheFileObject(self, path_spec, file_object):
    """Caches a file-like object based on a path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).
      file_object: the file-like object (instance of file_io.FileIO).
    """
    self._file_object_cache.CacheObject(path_spec, file_object)

  def CacheFileSystem(self, path_spec, file_system):
    """Caches a file system object based on a path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).
      file_system: the file system object (instance of vfs.FileSystem).
    """
    self._file_system_cache.CacheObject(path_spec, file_system)

  def GetFileObject(self, path_spec):
    """Retrieves a file-like object defined by path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).

    Returns:
      The file-like object (instance of file_io.FileIO) or None if not cached.
    """
    return self._file_object_cache.GetObject(path_spec)

  def GetFileSystem(self, path_spec):
    """Retrieves a file system object defined by path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).

    Returns:
      The file system object (instance of vfs.FileSystem) or None if not cached.
    """
    return self._file_system_cache.GetObject(path_spec)

  def RemoveFileObject(self, path_spec):
    """Removes a file-like object based on a path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).
    """
    self._file_object_cache.RemoveObject(path_spec)

  def RemoveFileSystem(self, path_spec):
    """Removes a file system object based on a path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).
    """
    self._file_system_cache.RemoveObject(path_spec)
