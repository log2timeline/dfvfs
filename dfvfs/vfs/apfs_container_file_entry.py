# -*- coding: utf-8 -*-
"""The APFS container file entry implementation."""

from dfvfs.lib import apfs_helper
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.resolver import resolver
from dfvfs.vfs import apfs_container_directory
from dfvfs.vfs import file_entry


class APFSContainerFileEntry(file_entry.FileEntry):
  """File system file entry that uses pyfsapfs."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_APFS_CONTAINER

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
          entry emulated by the corresponding file system.

    Raises:
      BackEndError: when the fsapfs volume is missing in a non-virtual
          file entry.
    """
    fsapfs_volume = file_system.GetAPFSVolumeByPathSpec(path_spec)
    if not is_virtual and fsapfs_volume is None:
      raise errors.BackEndError(
          'Missing fsapfs volume in non-virtual file entry.')

    super(APFSContainerFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._name = None
    self._fsapfs_volume = fsapfs_volume

    if self._is_virtual:
      self.entry_type = definitions.FILE_ENTRY_TYPE_DIRECTORY
    else:
      self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      APFSContainerDirectory: a directory.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return None

    return apfs_container_directory.APFSContainerDirectory(
        self._file_system, self.path_spec)

  def _GetSubFileEntries(self):
    """Retrieves a sub file entries generator.

    Yields:
      APFSContainerFileEntry: a sub file entry.
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield APFSContainerFileEntry(
            self._resolver_context, self._file_system, path_spec)

  # TODO: expose date and time values.

  @property
  def name(self):
    """str: name of the file entry, which does not include the full path."""
    if self._name is None:
      location = getattr(self.path_spec, 'location', None)
      if location is not None:
        self._name = self._file_system.BasenamePath(location)
      else:
        volume_index = apfs_helper.APFSContainerPathSpecGetVolumeIndex(
            self.path_spec)
        if volume_index is not None:
          apfs_volume_index = volume_index + 1
          self._name = f'apfs{apfs_volume_index:d}'
        else:
          self._name = ''

    return self._name

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    if self._fsapfs_volume is None:
      return None

    # TODO: change libfsapfs so self._fsapfs_volume.size works
    return 0

  @property
  def sub_file_entries(self):
    """generator[APFSContainerFileEntry]: sub file entries."""
    return self._GetSubFileEntries()

  def GetAPFSVolume(self):
    """Retrieves an APFS volume.

    Returns:
      pyfsapfs.volume: an APFS volume or None if not available.
    """
    return self._fsapfs_volume

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      APFSContainerFileEntry: parent file entry or None if not available.
    """
    volume_index = apfs_helper.APFSContainerPathSpecGetVolumeIndex(
        self.path_spec)
    if volume_index is None:
      return None

    return self._file_system.GetRootFileEntry()

  def IsLocked(self):
    """Determines if the file entry is locked.

    Returns:
      bool: True if the file entry is locked.
    """
    if self._fsapfs_volume is None:
      return False

    return self._fsapfs_volume.is_locked()

  def Unlock(self):
    """Unlocks the file entry.

    Returns:
      bool: True if the file entry was unlocked.
    """
    if not self._fsapfs_volume or not self._fsapfs_volume.is_locked():
      return True

    return apfs_helper.APFSUnlockVolume(
        self._fsapfs_volume, self.path_spec, resolver.Resolver.key_chain)
