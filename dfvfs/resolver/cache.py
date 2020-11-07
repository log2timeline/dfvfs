# -*- coding: utf-8 -*-
"""The resolver objects cache."""

from __future__ import unicode_literals

import collections
import itertools

from dfvfs.lib import errors


class ObjectsCacheValue(object):
  """Resolver object cache value."""

  def __init__(self, vfs_object):
    """Initializes the resolver objects cache value object.

    Args:
      vfs_object (object): VFS object to cache.
    """
    super(ObjectsCacheValue, self).__init__()
    self._reference_count = 0
    self.vfs_object = vfs_object

  @property
  def reference_count(self):
    """int: reference count."""
    return self._reference_count

  def DecrementReferenceCount(self):
    """Decrements the reference count.

    Raises:
      RuntimeError: if the reference count is 0.
    """
    if self._reference_count == 0:
      raise RuntimeError('Unable to decrement a reference count of 0.')

    self._reference_count -= 1

  def IncrementReferenceCount(self):
    """Increments the reference count."""
    self._reference_count += 1

  def IsDereferenced(self):
    """Checks if the cache value is dereferenced."""
    return self._reference_count == 0


class ObjectsCache(object):
  """Resolver object cache."""

  def __init__(self, maximum_number_of_cached_values):
    """Initializes the resolver objects cache object.

    Args:
      maximum_number_of_cached_values (int): maximum number of cached values.

    Raises:
      ValueError: when the maximum number of cached objects is 0 or less.
    """
    if maximum_number_of_cached_values <= 0:
      raise ValueError(
          'Invalid maximum number of cached objects value zero or less.')

    super(ObjectsCache, self).__init__()
    self._maximum_number_of_cached_values = maximum_number_of_cached_values
    self._values = collections.OrderedDict()

  def CacheObject(self, identifier, vfs_object):
    """Caches a VFS object.

    This method ignores the cache value reference count.

    Args:
      identifier (str): VFS object identifier.
      vfs_object (object): VFS object to cache.

    Raises:
      CacheFullError: if he maximum number of cached values is reached.
      KeyError: if the VFS object already is cached.
    """
    if identifier in self._values:
      raise KeyError('Object already cached for identifier: {0:s}'.format(
          identifier))

    if len(self._values) == self._maximum_number_of_cached_values:
      raise errors.CacheFullError('Maximum number of cached values reached.')

    self._values[identifier] = ObjectsCacheValue(vfs_object)

  def Empty(self):
    """Empties the cache.

    This method ignores the cache value reference count.
    """
    self._values.clear()

  def GetCacheValue(self, identifier):
    """Retrieves the cache value based on the identifier.

    Args:
      identifier (str): VFS object identifier.

    Returns:
      ObjectsCacheValue: cache value object or None if not cached.

    Raises:
      RuntimeError: if the cache value is missing.
    """
    return self._values.get(identifier, None)

  def GetCacheValueByObject(self, vfs_object):
    """Retrieves the cache value for the cached object.

    Args:
      vfs_object (object): VFS object that was cached.

    Returns:
      tuple[str, ObjectsCacheValue]: identifier and cache value object or
          (None, None) if not cached.

    Raises:
      RuntimeError: if the cache value is missing.
    """
    for identifier, cache_value in self._values.items():
      if not cache_value:
        raise RuntimeError('Missing cache value.')

      if cache_value.vfs_object == vfs_object:
        return identifier, cache_value

    return None, None

  def GetLastObject(self):
    """Retrieves the last cached object.

    This method ignores the cache value reference count.

    Returns:
      object: the last cached VFS object or None if the cache is empty.
    """
    if not self._values:
      return None

    # Get the last (or most recent added) cache value.
    cache_value = next(itertools.islice(
        self._values.values(), len(self._values) - 1, None))
    return cache_value.vfs_object

  def GetObject(self, identifier):
    """Retrieves a cached object based on the identifier.

    This method ignores the cache value reference count.

    Args:
      identifier (str): VFS object identifier.

    Returns:
      object: cached VFS object or None if not cached.
    """
    cache_value = self._values.get(identifier, None)
    if not cache_value:
      return None

    return cache_value.vfs_object

  def GrabObject(self, identifier):
    """Grabs a cached object based on the identifier.

    This method increments the cache value reference count.

    Args:
      identifier (str): VFS object identifier.

    Raises:
      KeyError: if the VFS object is not found in the cache.
      RuntimeError: if the cache value is missing.
    """
    if identifier not in self._values:
      raise KeyError('Missing cached object for identifier: {0:s}'.format(
          identifier))

    cache_value = self._values[identifier]
    if not cache_value:
      raise RuntimeError('Missing cache value for identifier: {0:s}'.format(
          identifier))

    cache_value.IncrementReferenceCount()

  def ReleaseObject(self, identifier):
    """Releases a cached object based on the identifier.

    This method decrements the cache value reference count.

    Args:
      identifier (str): VFS object identifier.

    Raises:
      KeyError: if the VFS object is not found in the cache.
      RuntimeError: if the cache value is missing.
    """
    if identifier not in self._values:
      raise KeyError('Missing cached object for identifier: {0:s}'.format(
          identifier))

    cache_value = self._values[identifier]
    if not cache_value:
      raise RuntimeError('Missing cache value for identifier: {0:s}'.format(
          identifier))

    cache_value.DecrementReferenceCount()

  def RemoveObject(self, identifier):
    """Removes a cached object based on the identifier.

    This method ignores the cache value reference count.

    Args:
      identifier (str): VFS object identifier.

    Raises:
      KeyError: if the VFS object is not found in the cache.
    """
    if identifier not in self._values:
      raise KeyError('Missing cached object for identifier: {0:s}'.format(
          identifier))

    del self._values[identifier]

  def SetMaximumNumberOfCachedValues(self, maximum_number_of_cached_values):
    """Sets the maximum number of cached values.

    Args:
      maximum_number_of_cached_values (int): maximum number of cached values.

    Raises:
      ValueError: when the maximum number of cached objects is 0 or less.
    """
    if maximum_number_of_cached_values <= 0:
      raise ValueError(
          'Invalid maximum number of cached objects value zero or less.')

    self._maximum_number_of_cached_values = maximum_number_of_cached_values
