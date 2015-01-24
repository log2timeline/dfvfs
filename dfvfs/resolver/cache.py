# -*- coding: utf-8 -*-
"""The resolver objects cache."""

import collections


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

  def CacheObject(self, identifier, vfs_object):
    """Caches a VFS object.

    Args:
      identifier: string that identifiers the VFS object.
      vfs_object: the VFS object to cache.
    """
    if len(self._vfs_objects) == self._maximum_number_of_cached_objects:
      lfu_identifier = self._vfs_objects_mru.pop()
      del self._vfs_objects[lfu_identifier]

    self._vfs_objects[identifier] = vfs_object
    self._vfs_objects_mru.appendleft(identifier)

  def Empty(self):
    """Empties the cache."""
    # Since we're changing the self._vfs_objects dict we cannot use iterkeys().
    for key in self._vfs_objects.keys():
      self._vfs_objects_mru.remove(key)
      del self._vfs_objects[key]

  def GetIdentifier(self, vfs_object):
    """Retrieves the identifier cached object.

    Args:
      vfs_object: the VFS object that was cached.

    Returns:
      The string that identifiers the VFS object or None.
    """
    for key, value in self._vfs_objects.iteritems():
      if vfs_object == value:
        return key

  def GetObject(self, identifier):
    """Retrieves a cached object based on the identifier.

    Args:
      identifier: string that identifiers the VFS object.

    Returns:
      The cached VFS object or None if not cached.
    """
    if identifier not in self._vfs_objects:
      return

    self._vfs_objects_mru.remove(identifier)
    self._vfs_objects_mru.appendleft(identifier)

    return self._vfs_objects[identifier]

  def RemoveObject(self, identifier):
    """Removes a cached object based on the identifier.

    Args:
      identifier: string that identifiers the VFS object.
    """
    if identifier not in self._vfs_objects:
      return

    self._vfs_objects_mru.remove(identifier)
    del self._vfs_objects[identifier]
