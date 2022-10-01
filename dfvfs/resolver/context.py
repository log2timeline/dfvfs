# -*- coding: utf-8 -*-
"""The resolver context object."""

import weakref

from dfvfs.mount import manager as mount_manager


class Context(object):
  """Resolver context."""

  def __init__(self):
    """Initializes the resolver context."""
    super(Context, self).__init__()
    # The WeakValueDictionary will maintain a (weak) reference to a VFS object
    # as long as the object is (strong) referrened by other objects. If an
    # object has no remaining (strong) references it is removed from the
    # WeakValueDictionary.
    self._file_object_cache = weakref.WeakValueDictionary()
    self._file_system_cache = weakref.WeakValueDictionary()
    self._mount_points = {}

  def _GetFileSystemCacheIdentifier(self, path_spec):
    """Determines the file system cache identifier for the path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      str: identifier of the VFS object.
    """
    string_parts = []

    string_parts.append(getattr(path_spec.parent, 'comparable', ''))
    string_parts.append(f'type: {path_spec.type_indicator:s}')

    return ''.join(string_parts)

  def DeregisterMountPoint(self, mount_point):
    """Deregisters a path specification mount point.

    Args:
      mount_point (str): mount point identifier.

    Raises:
      KeyError: if the corresponding mount point is not set.
    """
    if mount_point not in self._mount_points:
      raise KeyError(f'Mount point: {mount_point:s} not set.')

    del self._mount_points[mount_point]

  def CacheFileObject(self, path_spec, file_object):
    """Caches a file-like object based on a path specification.

    Args:
      path_spec (PathSpec): path specification.
      file_object (FileIO): file-like object.

    Raises:
      KeyError: if the file object already is cached.
    """
    identifier = path_spec.comparable

    if identifier in self._file_object_cache:
      raise KeyError(
          f'File object already cached for identifier: {identifier:s}')

    self._file_object_cache[identifier] = file_object

  def CacheFileSystem(self, path_spec, file_system):
    """Caches a file system object based on a path specification.

    Args:
      path_spec (PathSpec): path specification.
      file_system (FileSystem): file system object.

    Raises:
      KeyError: if the file system already is cached.
    """
    identifier = self._GetFileSystemCacheIdentifier(path_spec)

    if identifier in self._file_system_cache:
      raise KeyError(
          f'File system already cached for identifier: {identifier:s}')

    self._file_system_cache[identifier] = file_system

  def Empty(self):
    """Empties the caches."""
    self._file_object_cache.clear()
    self._file_system_cache.clear()

  def GetFileObject(self, path_spec):
    """Retrieves a file-like object defined by path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      FileIO: a file-like object or None if not cached.
    """
    return self._file_object_cache.get(path_spec.comparable, None)

  def GetFileSystem(self, path_spec):
    """Retrieves a file system object defined by path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      FileSystem: a file system object or None if not cached.
    """
    identifier = self._GetFileSystemCacheIdentifier(path_spec)
    return self._file_system_cache.get(identifier, None)

  def GetMountPoint(self, mount_point):
    """Retrieves the path specification of a mount point.

    Args:
      mount_point (str): mount point identifier.

    Returns:
      PathSpec: path specification of the mount point or None if the mount
          point does not exists.
    """
    path_spec = self._mount_points.get(mount_point, None)
    if not path_spec:
      path_spec = mount_manager.MountPointManager.GetMountPoint(mount_point)
    return path_spec

  def RegisterMountPoint(self, mount_point, path_spec):
    """Registers a path specification mount point.

    Args:
      mount_point (str): mount point identifier.
      path_spec (PathSpec): path specification of the mount point.

    Raises:
      KeyError: if the corresponding mount point is already set.
    """
    if mount_point in self._mount_points:
      raise KeyError(f'Mount point: {mount_point:s} already set.')

    self._mount_points[mount_point] = path_spec
