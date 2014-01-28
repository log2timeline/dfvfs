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
"""The resolver objects cache."""

import collections

from dfvfs.path import path_spec as dfvfs_path_spec


class ObjectsCache(object):
  """Class that implements the resolver object cache."""

  def __init__(self, maximum_number_of_cached_objects):
    """Initializes the resolver objects cache object.

    Args:
      maximum_number_of_cached_object: the maximum number of cached objects.

    Raises:
      ValueError: when the maximum number of cached objects is 0 or less.
    """
    if maximum_number_of_cached_objects <= 0:
      raise ValueError(
          u'Invalid maximum number of cached objects value zero or less.')

    super(ObjectsCache, self).__init__()
    self._maximum_number_of_cached_objects = maximum_number_of_cached_objects
    self._vfs_objects = {}
    self._vfs_objects_mru = collections.deque()

  def CacheObject(self, path_spec, vfs_object):
    """Caches a VFS object.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).
      vfs_object: the VFS object to cache.
    """
    if len(self._vfs_objects) == self._maximum_number_of_cached_objects:
      lfu_path_spec = self._vfs_objects_mru.pop()
      del self._vfs_objects[lfu_path_spec]

    self._vfs_objects[path_spec] = vfs_object
    self._vfs_objects_mru.appendleft(path_spec)

  def GetObject(self, path_spec):
    """Retrieves a cached object based on the path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).

    Returns:
      The cached VFS object or None if not cached.
    """
    if path_spec not in self._vfs_objects:
      return

    self._vfs_objects_mru.remove(path_spec)
    self._vfs_objects_mru.appendleft(path_spec)

    return self._vfs_objects[path_spec]

  def RemoveObject(self, vfs_object):
    """Removes a cached object based on the path specification.

    Args:
      vfs_object: the VFS path specification (instance of path.PathSpec)
                  or VFS object that was cached.
    """
    if isinstance(vfs_object, dfvfs_path_spec.PathSpec):
      if vfs_object not in self._vfs_objects:
        return

      path_spec = vfs_object

    else:
      path_spec = None
      for key, value in self._vfs_objects.iteritems():
        if vfs_object == value:
          path_spec = key
          break

      if not path_spec:
        return

    self._vfs_objects_mru.remove(path_spec)

    del self._vfs_objects[path_spec]
