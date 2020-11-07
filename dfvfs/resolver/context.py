# -*- coding: utf-8 -*-
"""The resolver context object."""

from __future__ import unicode_literals

from dfvfs.resolver import cache


class Context(object):
  """Resolver context."""

  def __init__(
      self, maximum_number_of_file_objects=128,
      maximum_number_of_file_systems=16):
    """Initializes the resolver context object.

    Args:
      maximum_number_of_file_objects (Optional[int]): maximum number
          of file-like objects cached in the context.
      maximum_number_of_file_systems (Optional[int]): maximum number
          of file system objects cached in the context.
    """
    super(Context, self).__init__()
    self._file_object_cache = cache.ObjectsCache(
        maximum_number_of_file_objects)
    self._file_system_cache = cache.ObjectsCache(
        maximum_number_of_file_systems)

  def _GetFileSystemCacheIdentifier(self, path_spec):
    """Determines the file system cache identifier for the path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      str: identifier of the VFS object.
    """
    string_parts = []

    string_parts.append(getattr(path_spec.parent, 'comparable', ''))
    string_parts.append('type: {0:s}'.format(path_spec.type_indicator))

    return ''.join(string_parts)

  def CacheFileObject(self, path_spec, file_object):
    """Caches a file-like object based on a path specification.

    Args:
      path_spec (PathSpec): path specification.
      file_object (FileIO): file-like object.
    """
    self._file_object_cache.CacheObject(path_spec.comparable, file_object)

  def CacheFileSystem(self, path_spec, file_system):
    """Caches a file system object based on a path specification.

    Args:
      path_spec (PathSpec): path specification.
      file_system (FileSystem): file system object.
    """
    identifier = self._GetFileSystemCacheIdentifier(path_spec)
    self._file_system_cache.CacheObject(identifier, file_system)

  def Empty(self):
    """Empties the caches."""
    file_object = self._file_object_cache.GetLastObject()
    while file_object:
      file_object.close()
      file_object = self._file_object_cache.GetLastObject()

    self._file_object_cache.Empty()
    self._file_system_cache.Empty()

  def ForceRemoveFileObject(self, path_spec):
    """Forces the removal of a file-like object based on a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      bool: True if the file-like object was cached.
    """
    cache_value = self._file_object_cache.GetCacheValue(path_spec.comparable)
    if not cache_value:
      return False

    while not cache_value.IsDereferenced():
      cache_value.vfs_object.close()

    return True

  def GetFileObject(self, path_spec):
    """Retrieves a file-like object defined by path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      FileIO: a file-like object or None if not cached.
    """
    return self._file_object_cache.GetObject(path_spec.comparable)

  def GetFileObjectReferenceCount(self, path_spec):
    """Retrieves the reference count of a cached file-like object.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      int: reference count or None if there is no file-like object for
          the corresponding path specification cached.
    """
    cache_value = self._file_object_cache.GetCacheValue(path_spec.comparable)
    if not cache_value:
      return None

    return cache_value.reference_count

  def GetFileSystem(self, path_spec):
    """Retrieves a file system object defined by path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      FileSystem: a file system object or None if not cached.
    """
    identifier = self._GetFileSystemCacheIdentifier(path_spec)
    return self._file_system_cache.GetObject(identifier)

  def GetFileSystemReferenceCount(self, path_spec):
    """Retrieves the reference count of a cached file system object.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      int: reference count or None if there is no file system object for
          the corresponding path specification cached.
    """
    identifier = self._GetFileSystemCacheIdentifier(path_spec)
    cache_value = self._file_system_cache.GetCacheValue(identifier)
    if not cache_value:
      return None

    return cache_value.reference_count

  def GrabFileObject(self, path_spec):
    """Grabs a cached file-like object defined by path specification.

    Args:
      path_spec (PathSpec): path specification.
    """
    self._file_object_cache.GrabObject(path_spec.comparable)

  def GrabFileSystem(self, path_spec):
    """Grabs a cached file system object defined by path specification.

    Args:
      path_spec (PathSpec): path specification.
    """
    identifier = self._GetFileSystemCacheIdentifier(path_spec)
    self._file_system_cache.GrabObject(identifier)

  def ReleaseFileObject(self, file_object):
    """Releases a cached file-like object.

    Args:
      file_object (FileIO): file-like object.

    Returns:
      bool: True if the file-like object can be closed.

    Raises:
      PathSpecError: if the path specification is incorrect.
      RuntimeError: if the file-like object is not cached or an inconsistency
          is detected in the cache.
    """
    identifier, cache_value = self._file_object_cache.GetCacheValueByObject(
        file_object)

    if not identifier:
      raise RuntimeError('Object not cached.')

    if not cache_value:
      raise RuntimeError('Invalid cache value.')

    self._file_object_cache.ReleaseObject(identifier)

    result = cache_value.IsDereferenced()
    if result:
      self._file_object_cache.RemoveObject(identifier)

    return result

  def ReleaseFileSystem(self, file_system):
    """Releases a cached file system object.

    Args:
      file_system (FileSystem): file system object.

    Returns:
      bool: True if the file system object can be closed.

    Raises:
      PathSpecError: if the path specification is incorrect.
      RuntimeError: if the file system object is not cached or an inconsistency
          is detected in the cache.
    """
    identifier, cache_value = self._file_system_cache.GetCacheValueByObject(
        file_system)

    if not identifier:
      raise RuntimeError('Object not cached.')

    if not cache_value:
      raise RuntimeError('Invalid cache value.')

    self._file_system_cache.ReleaseObject(identifier)

    result = cache_value.IsDereferenced()
    if result:
      self._file_system_cache.RemoveObject(identifier)

    return result

  def SetMaximumNumberOfFileObjects(self, maximum_number_of_file_objects):
    """Sets the maximum number of cached file-like objects.

    Args:
      maximum_number_of_file_objects (int): maximum number of file-like
          objects cached in the context.
    """
    self._file_object_cache.SetMaximumNumberOfCachedValues(
        maximum_number_of_file_objects)

  def SetMaximumNumberOfFileSystems(self, maximum_number_of_file_systems):
    """Sets the maximum number of cached file system objects.

    Args:
      maximum_number_of_file_systems (int): maximum number of file system
          objects cached in the context.
    """
    self._file_system_cache.SetMaximumNumberOfCachedValues(
        maximum_number_of_file_systems)
