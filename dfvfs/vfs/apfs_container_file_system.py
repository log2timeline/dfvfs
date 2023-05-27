# -*- coding: utf-8 -*-
"""The APFS container file system implementation."""

import pyfsapfs

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import apfs_container_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import apfs_container_file_entry
from dfvfs.vfs import file_system


class APFSContainerFileSystem(file_system.FileSystem):
  """APFS container file system using pyfsapfs."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_APFS_CONTAINER

  _APFS_LOCATION_PREFIX = '/apfs'

  def __init__(self, resolver_context, path_spec):
    """Initializes an APFS container file system.

    Args:
      resolver_context (resolver.Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(APFSContainerFileSystem, self).__init__(resolver_context, path_spec)
    self._file_object = None
    self._fsapfs_container = None

  def _Close(self):
    """Closes the file system.

    Raises:
      IOError: if the close failed.
    """
    self._fsapfs_container = None
    self._file_object = None

  def _Open(self, mode='rb'):
    """Opens the file system defined by path specification.

    Args:
      mode (Optional[str])): file access mode. The default is 'rb' read-only
          binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not self._path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    file_object = resolver.Resolver.OpenFileObject(
        self._path_spec.parent, resolver_context=self._resolver_context)

    fsapfs_container = pyfsapfs.container()
    fsapfs_container.open_file_object(file_object)

    self._file_object = file_object
    self._fsapfs_container = fsapfs_container

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      bool: True if the file entry exists.
    """
    volume_index = self.GetVolumeIndexByPathSpec(path_spec)

    # The virtual root file has no corresponding volume index but
    # should have a location.
    if volume_index is None:
      location = getattr(path_spec, 'location', None)
      return location is not None and location == self.LOCATION_ROOT

    return 0 <= volume_index < self._fsapfs_container.number_of_volumes

  def GetAPFSContainer(self):
    """Retrieves the APFS container.

    Returns:
      pyfsapfs.container: the APFS container.
    """
    return self._fsapfs_container

  def GetAPFSVolumeByPathSpec(self, path_spec):
    """Retrieves an APFS volume for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      pyfsapfs.volume: an APFS volume or None if not available.
    """
    volume_index = self.GetVolumeIndexByPathSpec(path_spec)
    if volume_index is None:
      return None

    return self._fsapfs_container.get_volume(volume_index)

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      APFSContainerFileEntry: a file entry or None if not exists.
    """
    volume_index = self.GetVolumeIndexByPathSpec(path_spec)

    # The virtual root file has no corresponding volume index but
    # should have a location.
    if volume_index is None:
      location = getattr(path_spec, 'location', None)
      if location is None or location != self.LOCATION_ROOT:
        return None

      return apfs_container_file_entry.APFSContainerFileEntry(
          self._resolver_context, self, path_spec, is_root=True,
          is_virtual=True)

    if (volume_index < 0 or
        volume_index >= self._fsapfs_container.number_of_volumes):
      return None

    return apfs_container_file_entry.APFSContainerFileEntry(
        self._resolver_context, self, path_spec, volume_index=volume_index)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      APFSContainerFileEntry: a file entry.
    """
    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location=self.LOCATION_ROOT, parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)

  def GetVolumeIndexByPathSpec(self, path_spec):
    """Retrieves the volume index for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      int: volume index or None if the index cannot be determined.
    """
    volume_index = getattr(path_spec, 'volume_index', None)
    if volume_index is not None:
      return volume_index

    location = getattr(path_spec, 'location', None)
    if location is None or location[:5] != self._APFS_LOCATION_PREFIX:
      return None

    volume_index = None

    if len(location) > 6 and location[5] == '{' and location[-1] == '}':
      for index, fsapfs_volume in enumerate(
          self._fsapfs_container.volumes):
        if fsapfs_volume.identifier == location[6:-1]:
          volume_index = index
          break

    else:
      try:
        volume_index = int(location[5:], 10) - 1
      except (TypeError, ValueError):
        pass

    if volume_index is None or volume_index < 0 or volume_index > 99:
      volume_index = None

    return volume_index
