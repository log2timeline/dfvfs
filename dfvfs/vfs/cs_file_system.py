# -*- coding: utf-8 -*-
"""The Core Storage (CS) file system implementation."""

import pyfvde

from dfvfs.lib import cs_helper
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import cs_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import cs_file_entry
from dfvfs.vfs import file_system


class CSFileSystem(file_system.FileSystem):
  """File system that uses pyfvde."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_CS

  def __init__(self, resolver_context, path_spec):
    """Initializes a file system.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(CSFileSystem, self).__init__(resolver_context, path_spec)
    self._fvde_volume = None
    self._fvde_volume_group = None
    self._file_object = None

  def _Close(self):
    """Closes the file system.

    Raises:
      IOError: if the close failed.
    """
    self._fvde_volume_group = None
    self._fvde_volume.close()
    self._fvde_volume = None
    self._file_object = None

  def _Open(self, mode='rb'):
    """Opens the file system defined by path specification.

    Args:
      mode (Optional[str]): file access mode. The default is 'rb'
          read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not self._path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    resolver.Resolver.key_chain.ExtractCredentialsFromPathSpec(self._path_spec)

    file_object = resolver.Resolver.OpenFileObject(
        self._path_spec.parent, resolver_context=self._resolver_context)

    fvde_volume = pyfvde.volume()

    encrypted_root_plist = resolver.Resolver.key_chain.GetCredential(
        self._path_spec, 'encrypted_root_plist')
    if encrypted_root_plist:
      fvde_volume.read_encrypted_root_plist(encrypted_root_plist)

    fvde_volume.open_file_object(file_object)
    # TODO: implement multi physical volume support.
    fvde_volume.open_physical_volume_files_as_file_objects([file_object])
    fvde_volume_group = fvde_volume.get_volume_group()

    self._file_object = file_object
    self._fvde_volume = fvde_volume
    self._fvde_volume_group = fvde_volume_group

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      bool: True if the file entry exists.
    """
    volume_index = cs_helper.CSPathSpecGetVolumeIndex(path_spec)

    # The virtual root file has no corresponding volume index but
    # should have a location.
    if volume_index is None:
      location = getattr(path_spec, 'location', None)
      return location is not None and location == self.LOCATION_ROOT

    return (
        0 <= volume_index < self._fvde_volume_group.number_of_logical_volumes)

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      CSFileEntry: a file entry or None if not available.
    """
    volume_index = cs_helper.CSPathSpecGetVolumeIndex(path_spec)

    # The virtual root file has no corresponding volume index but
    # should have a location.
    if volume_index is None:
      location = getattr(path_spec, 'location', None)
      if location is None or location != self.LOCATION_ROOT:
        return None

      return cs_file_entry.CSFileEntry(
          self._resolver_context, self, path_spec, is_root=True,
          is_virtual=True)

    if (volume_index < 0 or
        volume_index >= self._fvde_volume_group.number_of_logical_volumes):
      return None

    return cs_file_entry.CSFileEntry(
        self._resolver_context, self, path_spec)

  def GetFVDELogicalVolumeByPathSpec(self, path_spec):
    """Retrieves a Core Storage logical volume for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      pyfvde.logical_volume: a Core Storage logical volume or None if not
          available.
    """
    volume_index = cs_helper.CSPathSpecGetVolumeIndex(path_spec)
    if volume_index is None:
      return None

    return self._fvde_volume_group.get_logical_volume(volume_index)

  def GetFVDEVolumeGroup(self):
    """Retrieves the Core Storage volume group.

    Returns:
      pyfvde.volume_group: a Core Storage volume group.
    """
    return self._fvde_volume_group

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      CSFileEntry: root file entry or None if not available.
    """
    path_spec = cs_path_spec.CSPathSpec(
        location=self.LOCATION_ROOT, parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
