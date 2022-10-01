# -*- coding: utf-8 -*-
"""The Logical Volume Manager (LVM) file entry implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import lvm_helper
from dfvfs.vfs import file_entry
from dfvfs.vfs import lvm_directory


class LVMFileEntry(file_entry.FileEntry):
  """File system file entry that uses pyvslvm."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_LVM

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False, vslvm_logical_volume=None):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
      vslvm_logical_volume (Optional[pyvslvm.logical_volume]): a LVM logical
          volume.

    Raises:
      BackEndError: when LVM logical volume is missing for a non-virtual file
          entry.
    """
    if not is_virtual and vslvm_logical_volume is None:
      vslvm_logical_volume = file_system.GetLVMLogicalVolumeByPathSpec(
          path_spec)
    if not is_virtual and vslvm_logical_volume is None:
      raise errors.BackEndError(
          'Missing vslvm logical volume in non-virtual file entry.')

    super(LVMFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._name = None
    self._vslvm_logical_volume = vslvm_logical_volume

    if self._is_virtual:
      self.entry_type = definitions.FILE_ENTRY_TYPE_DIRECTORY
    else:
      self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  def _GetDirectory(self):
    """Retrieves the directory.

    Returns:
      LVMDirectory: a directory.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return None

    return lvm_directory.LVMDirectory(self._file_system, self.path_spec)

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      LVMFileEntry: a sub file entry.
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield LVMFileEntry(self._resolver_context, self._file_system, path_spec)

  # TODO: implement creation_time property after implementing
  # vslvm_logical_volume.get_creation_time_as_integer()

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
          lvm_volume_index = volume_index + 1
          self._name = f'lvm{lvm_volume_index:d}'
        else:
          self._name = ''

    return self._name

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    if self._vslvm_logical_volume is None:
      return None

    return self._vslvm_logical_volume.size

  def GetLVMLogicalVolume(self):
    """Retrieves the LVM logical volume.

    Returns:
      pyvslvm.logical_volume: a LVM logical volume.
    """
    return self._vslvm_logical_volume

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      LVMFileEntry: parent file entry or None if not available.
    """
    volume_index = lvm_helper.LVMPathSpecGetVolumeIndex(self.path_spec)
    if volume_index is None:
      return None

    return self._file_system.GetRootFileEntry()
