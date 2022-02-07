# -*- coding: utf-8 -*-
"""The resolver objects cache."""

import weakref

from dfvfs.lib import errors


class ObjectsCache(object):
  """Resolver object cache."""

  def __init__(self, maximum_number_of_cached_values):
    """Initializes a resolver objects cache object.

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
    # The WeakValueDictionary will maintain a (weak) reference to a VFS object
    # as long as the object is (strong) referrened by other objects. If an
    # object has no remaining (strong) references it is removed from the
    # WeakValueDictionary.
    self._values = weakref.WeakValueDictionary()

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

    self._values[identifier] = vfs_object

  def Empty(self):
    """Empties the cache.

    This method ignores the cache value reference count.
    """
    self._values.clear()

  def GetObject(self, identifier):
    """Retrieves a cached object based on the identifier.

    This method ignores the cache value reference count.

    Args:
      identifier (str): VFS object identifier.

    Returns:
      object: cached VFS object or None if not cached.
    """
    return self._values.get(identifier, None)

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
