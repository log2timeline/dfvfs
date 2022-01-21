# -*- coding: utf-8 -*-
"""The Volume Shadow Snapshots (VSS) file system implementation."""

import pyvshadow

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import vshadow_helper
from dfvfs.path import vshadow_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system
from dfvfs.vfs import vshadow_file_entry


class VShadowFileSystem(file_system.FileSystem):
  """File system that uses pyvshadow."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VSHADOW

  def __init__(self, resolver_context, path_spec):
    """Initializes a file system.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(VShadowFileSystem, self).__init__(resolver_context, path_spec)
    self._file_object = None
    self._vshadow_volume = None

  def _Close(self):
    """Closes the file system.

    Raises:
      IOError: if the close failed.
    """
    self._vshadow_volume.close()
    self._vshadow_volume = None
    self._file_object = None

  def _Open(self, mode='rb'):
    """Opens the file system object defined by path specification.

    Args:
      mode (Optional[str]): file access mode. The default is 'rb' which
          represents read-only binary.

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

    vshadow_volume = pyvshadow.volume()
    vshadow_volume.open_file_object(file_object)

    self._file_object = file_object
    self._vshadow_volume = vshadow_volume

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      bool: True if the file entry exists.
    """
    store_index = vshadow_helper.VShadowPathSpecGetStoreIndex(path_spec)

    # The virtual root file has no corresponding store index but
    # should have a location.
    if store_index is None:
      location = getattr(path_spec, 'location', None)
      return location is not None and location == self.LOCATION_ROOT

    return 0 <= store_index < self._vshadow_volume.number_of_stores

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      VShadowFileEntry: file entry or None if not available.
    """
    store_index = vshadow_helper.VShadowPathSpecGetStoreIndex(path_spec)

    # The virtual root file has no corresponding store index but
    # should have a location.
    if store_index is None:
      location = getattr(path_spec, 'location', None)
      if location is None or location != self.LOCATION_ROOT:
        return None

      return vshadow_file_entry.VShadowFileEntry(
          self._resolver_context, self, path_spec, is_root=True,
          is_virtual=True)

    if store_index < 0 or store_index >= self._vshadow_volume.number_of_stores:
      return None

    return vshadow_file_entry.VShadowFileEntry(
        self._resolver_context, self, path_spec)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      VShadowFileEntry: file entry or None if not available.
    """
    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=self.LOCATION_ROOT, parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)

  def GetVShadowStoreByPathSpec(self, path_spec):
    """Retrieves a VSS store for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      pyvshadow.store: a VSS store or None if not available.
    """
    store_index = vshadow_helper.VShadowPathSpecGetStoreIndex(path_spec)
    if store_index is None:
      return None

    return self._vshadow_volume.get_store(store_index)

  def GetVShadowVolume(self):
    """Retrieves a VSS volume.

    Returns:
      pyvshadow.volume: a VSS volume.
    """
    return self._vshadow_volume
