# -*- coding: utf-8 -*-
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

  def _GetFileSystemCacheIdentifier(self, path_spec):
    """Determines the file system cache identifier for the path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).

    Returns:
      The string that identifiers the VFS object.
    """
    string_parts = []

    string_parts.append(getattr(path_spec.parent, u'comparable', u''))
    string_parts.append(u'type: {0:s}'.format(path_spec.type_indicator))

    return u''.join(string_parts)

  def CacheFileObject(self, path_spec, file_object):
    """Caches a file-like object based on a path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).
      file_object: the file-like object (instance of FileIO).
    """
    self._file_object_cache.CacheObject(path_spec.comparable, file_object)

  def CacheFileSystem(self, path_spec, file_system):
    """Caches a file system object based on a path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).
      file_system: the file system object (instance of vfs.FileSystem).
    """
    identifier = self._GetFileSystemCacheIdentifier(path_spec)
    self._file_system_cache.CacheObject(identifier, file_system)

  def Empty(self):
    """Empties the caches."""
    self._file_object_cache.Empty()
    self._file_system_cache.Empty()

  def ForceRemoveFileObject(self, path_spec):
    """Forces the removal of a file-like object based on a path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).

    Returns:
      A boolean that indicates the file-like object was cached or not.
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
      path_spec: the path specification (instance of PathSpec).

    Returns:
      The file-like object (instance of FileIO) or None if not cached.
    """
    return self._file_object_cache.GetObject(path_spec.comparable)

  def GetFileObjectReferenceCount(self, path_spec):
    """Retrieves the reference count of a cached file-like object.

    Args:
      path_spec: the path specification (instance of PathSpec).

    Returns:
      An integer containing the reference count or None if there is no
      file-like object for the corresponding path specification cached.
    """
    cache_value = self._file_object_cache.GetCacheValue(path_spec.comparable)
    if not cache_value:
      return

    return cache_value.reference_count

  def GetFileSystem(self, path_spec):
    """Retrieves a file system object defined by path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).

    Returns:
      The file system object (instance of vfs.FileSystem) or None if not cached.
    """
    identifier = self._GetFileSystemCacheIdentifier(path_spec)
    return self._file_system_cache.GetObject(identifier)

  def GetFileSystemReferenceCount(self, path_spec):
    """Retrieves the reference count of a cached file system object.

    Args:
      path_spec: the path specification (instance of PathSpec).

    Returns:
      An integer containing the reference count or None if there is no
      file system for the corresponding path specification cached.
    """
    identifier = self._GetFileSystemCacheIdentifier(path_spec)
    cache_value = self._file_system_cache.GetCacheValue(identifier)
    if not cache_value:
      return

    return cache_value.reference_count

  def GrabFileObject(self, path_spec):
    """Grabs a cached file-like object defined by path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).
    """
    self._file_object_cache.GrabObject(path_spec.comparable)

  def GrabFileSystem(self, path_spec):
    """Grabs a cached file system object defined by path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).
    """
    identifier = self._GetFileSystemCacheIdentifier(path_spec)
    self._file_system_cache.GrabObject(identifier)

  def ReleaseFileObject(self, file_object):
    """Releases a cached file-like object.

    Args:
      file_object: the file-like object (instance of FileIO).

    Returns:
      A boolean value indicating true if the file-like object can be closed.

    Raises:
      PathSpecError: if the path specification is incorrect.
      RuntimeError: if the file-like object is not cached or an inconsistency
                    is detected in the cache.
    """
    identifier, cache_value = self._file_object_cache.GetCacheValueByObject(
        file_object)

    if not identifier:
      raise RuntimeError(u'Object not cached.')

    if not cache_value:
      raise RuntimeError(u'Invalid cache value.')

    self._file_object_cache.ReleaseObject(identifier)

    result = cache_value.IsDereferenced()
    if result:
      self._file_object_cache.RemoveObject(identifier)

    return result

  def ReleaseFileSystem(self, file_system):
    """Releases a cached file system object.

    Args:
      file_system: the file systemobject (instance of vfs.FileSystem).

    Returns:
      A boolean value indicating true if the file system object can be closed.

    Raises:
      PathSpecError: if the path specification is incorrect.
      RuntimeError: if the file system object is not cached or an inconsistency
                    is detected in the cache.
    """
    identifier, cache_value = self._file_system_cache.GetCacheValueByObject(
        file_system)

    if not identifier:
      raise RuntimeError(u'Object not cached.')

    if not cache_value:
      raise RuntimeError(u'Invalid cache value.')

    self._file_system_cache.ReleaseObject(identifier)

    result = cache_value.IsDereferenced()
    if result:
      self._file_system_cache.RemoveObject(identifier)

    return result

  def SetMaximumNumberOfFileObjects(self, maximum_number_of_file_objects):
    """Sets the maximum number of cached filei-like objects.

    Args:
      maximum_number_of_file_objects: the maximum number of file-like
                                      objects cached in the context.
    """
    self._file_object_cache.SetMaximumNumberOfCachedValues(
        maximum_number_of_file_objects)

  def SetMaximumNumberOfFileSystems(self, maximum_number_of_file_systems):
    """Sets the maximum number of cached file system objects.

    Args:
      maximum_number_of_file_systems: the maximum number of file system
                                      objects cached in the context.
    """
    self._file_system_cache.SetMaximumNumberOfCachedValues(
        maximum_number_of_file_systems)
