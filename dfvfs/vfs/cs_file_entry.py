# -*- coding: utf-8 -*-
"""The Core Storage (CS) file entry implementation."""

from dfvfs.lib import cs_helper
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.resolver import resolver
from dfvfs.vfs import cs_directory
from dfvfs.vfs import file_entry


class CSFileEntry(file_entry.FileEntry):
  """File system file entry that uses pyfvde."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_CS

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False, fvde_logical_volume=None):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
      fvde_logical_volume (Optional[pyfvde.logical_volume]): a Core Storage
          logical volume.

    Raises:
      BackEndError: when Core Storage logical volume is missing for
          a non-virtual file entry.
    """
    if not is_virtual and fvde_logical_volume is None:
      fvde_logical_volume = file_system.GetFVDELogicalVolumeByPathSpec(
          path_spec)
    if not is_virtual and fvde_logical_volume is None:
      raise errors.BackEndError(
          'Missing fvde logical volume in non-virtual file entry.')

    super(CSFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._name = None
    self._fvde_logical_volume = fvde_logical_volume

    if self._is_virtual:
      self.entry_type = definitions.FILE_ENTRY_TYPE_DIRECTORY
    else:
      self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  def _GetDirectory(self):
    """Retrieves the directory.

    Returns:
      CSDirectory: a directory.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return None

    return cs_directory.CSDirectory(self._file_system, self.path_spec)

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      CSFileEntry: a sub file entry.
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield CSFileEntry(self._resolver_context, self._file_system, path_spec)

  @property
  def name(self):
    """str: name of the file entry, without the full path."""
    if self._name is None:
      location = getattr(self.path_spec, 'location', None)
      if location is not None:
        self._name = self._file_system.BasenamePath(location)
      else:
        volume_index = getattr(self.path_spec, 'volume_index', None)
        if volume_index is not None:
          cs_volume_index = volume_index + 1
          self._name = f'cs{cs_volume_index:d}'
        else:
          self._name = ''

    return self._name

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    if self._fvde_logical_volume is None:
      return None

    return self._fvde_logical_volume.size

  def GetFVDELogicalVolume(self):
    """Retrieves the Core Storage logical volume.

    Returns:
      pyfvde.logical_volume: a Core Storage logical volume.
    """
    return self._fvde_logical_volume

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      CSFileEntry: parent file entry or None if not available.
    """
    volume_index = cs_helper.CSPathSpecGetVolumeIndex(self.path_spec)
    if volume_index is None:
      return None

    return self._file_system.GetRootFileEntry()

  def IsLocked(self):
    """Determines if the file entry is locked.

    Returns:
      bool: True if the file entry is locked.
    """
    if not self._fvde_logical_volume:
      return False

    return self._fvde_logical_volume.is_locked()

  def Unlock(self):
    """Unlocks the file entry.

    Returns:
      bool: True if the file entry was unlocked.
    """
    if (not self._fvde_logical_volume or
        not self._fvde_logical_volume.is_locked()):
      return True

    return cs_helper.CSUnlockLogicalVolume(
        self._fvde_logical_volume, self.path_spec, resolver.Resolver.key_chain)
