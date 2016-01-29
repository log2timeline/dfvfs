# -*- coding: utf-8 -*-
"""The resolver objects cache."""

from dfvfs.lib import errors


class ObjectsCacheValue(object):
  """Class that implements the resolver object cache value."""

  def __init__(self, vfs_object):
    """Initializes the resolver objects cache value object.

    Args:
      vfs_object: the cached VFS object.
    """
    super(ObjectsCacheValue, self).__init__()
    self._reference_count = 0
    self.vfs_object = vfs_object

  @property
  def reference_count(self):
    """The reference count."""
    return self._reference_count

  def DecrementReferenceCount(self):
    """Decrements the reference count.

    Raises:
      RuntimeError: if the reference count is 0.
    """
    if self._reference_count == 0:
      raise RuntimeError(u'Unable to decrement a reference count of 0.')

    self._reference_count -= 1

  def IncrementReferenceCount(self):
    """Increments the reference count."""
    self._reference_count += 1

  def IsDereferenced(self):
    """Checks if the cache value is dereferenced."""
    return self._reference_count == 0


class ObjectsCache(object):
  """Class that implements the resolver object cache."""

  def __init__(self, maximum_number_of_cached_values):
    """Initializes the resolver objects cache object.

    Args:
      maximum_number_of_cached_values: the maximum number of cached values.

    Raises:
      ValueError: when the maximum number of cached objects is 0 or less.
    """
    if maximum_number_of_cached_values <= 0:
      raise ValueError(
          u'Invalid maximum number of cached objects value zero or less.')

    super(ObjectsCache, self).__init__()
    self._maximum_number_of_cached_values = maximum_number_of_cached_values
    self._values = {}

  def CacheObject(self, identifier, vfs_object):
    """Caches a VFS object.

    This method ignores the cache value reference count.

    Args:
      identifier: string that identifies the VFS object.
      vfs_object: the VFS object to cache.

    Raises:
      CacheFullError: if he maximum number of cached values is reached.
      KeyError: if the VFS object already is cached.
    """
    if identifier in self._values:
      raise KeyError(u'Object already cached for identifier: {0:s}'.format(
          identifier))

    if len(self._values) == self._maximum_number_of_cached_values:
      raise errors.CacheFullError(u'Maximum number of cached values reached.')

    self._values[identifier] = ObjectsCacheValue(vfs_object)

  def Empty(self):
    """Empties the cache.

    This method ignores the cache value reference count.
    """
    self._values.clear()

  def GetCacheValue(self, identifier):
    """Retrieves the cache value based on the identifier.

    Args:
      identifier: string that identifies the VFS object.

    Returns:
      The cache value object (instance of ObjectsCacheValue) or
      None if not cached.

    Raises:
      RuntimeError: if the cache value is missing.
    """
    return self._values.get(identifier, None)

  def GetCacheValueByObject(self, vfs_object):
    """Retrieves the cache value for the cached object.

    Args:
      vfs_object: the VFS object that was cached.

    Returns:
      A tuple of the string that identifies the VFS object and
      the cache value object (instance of ObjectsCacheValue) or
      None if not cached.

    Raises:
      RuntimeError: if the cache value is missing.
    """
    for identifier, cache_value in iter(self._values.items()):
      if not cache_value:
        raise RuntimeError(u'Missing cache value.')

      if cache_value.vfs_object == vfs_object:
        return identifier, cache_value

    return None, None

  def GetObject(self, identifier):
    """Retrieves a cached object based on the identifier.

    This method ignores the cache value reference count.

    Args:
      identifier: string that identifies the VFS object.

    Returns:
      The cached VFS object or None if not cached.
    """
    cache_value = self._values.get(identifier, None)
    if not cache_value:
      return

    return cache_value.vfs_object

  def GrabObject(self, identifier):
    """Grabs a cached object based on the identifier.

    This method increments the cache value reference count.

    Args:
      identifier: string that identifies the VFS object.

    Raises:
      KeyError: if the VFS object is not found in the cache.
      RuntimeError: if the cache value is missing.
    """
    if identifier not in self._values:
      raise KeyError(u'Missing cached object for identifier: {0:s}'.format(
          identifier))

    cache_value = self._values[identifier]
    if not cache_value:
      raise RuntimeError(u'Missing cache value for identifier: {0:s}'.format(
          identifier))

    cache_value.IncrementReferenceCount()

  def ReleaseObject(self, identifier):
    """Releases a cached object based on the identifier.

    This method decrements the cache value reference count.

    Args:
      identifier: string that identifies the VFS object.

    Raises:
      KeyError: if the VFS object is not found in the cache.
      RuntimeError: if the cache value is missing.
    """
    if identifier not in self._values:
      raise KeyError(u'Missing cached object for identifier: {0:s}'.format(
          identifier))

    cache_value = self._values[identifier]
    if not cache_value:
      raise RuntimeError(u'Missing cache value for identifier: {0:s}'.format(
          identifier))

    cache_value.DecrementReferenceCount()

  def RemoveObject(self, identifier):
    """Removes a cached object based on the identifier.

    This method ignores the cache value reference count.

    Args:
      identifier: string that identifies the VFS object.

    Raises:
      KeyError: if the VFS object is not found in the cache.
    """
    if identifier not in self._values:
      raise KeyError(u'Missing cached object for identifier: {0:s}'.format(
          identifier))

    del self._values[identifier]

  def SetMaximumNumberOfCachedValues(self, maximum_number_of_cached_values):
    """Sets the maximum number of cached values.

    Args:
      maximum_number_of_cached_values: the maximum number of cached values.

    Raises:
      ValueError: when the maximum number of cached objects is 0 or less.
    """
    if maximum_number_of_cached_values <= 0:
      raise ValueError(
          u'Invalid maximum number of cached objects value zero or less.')

    self._maximum_number_of_cached_values = maximum_number_of_cached_values
