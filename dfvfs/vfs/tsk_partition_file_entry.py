# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) partition file entry implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import tsk_partition
from dfvfs.vfs import file_entry
from dfvfs.vfs import tsk_partition_directory


class TSKPartitionFileEntry(file_entry.FileEntry):
  """File system file entry that uses pytsk3."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK_PARTITION

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False, tsk_vs_part=None):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
          entry emulated by the corresponding file system.
      tsk_vs_part (Optional[pytsk3.TSK_VS_PART_INFO]): TSK volume system part.

    Raises:
      BackEndError: when the TSK volume system part is missing in a non-virtual
          file entry.
    """
    tsk_volume = file_system.GetTSKVolume()
    if not is_virtual and tsk_vs_part is None:
      tsk_vs_part, _ = tsk_partition.GetTSKVsPartByPathSpec(
          tsk_volume, path_spec)
    if not is_virtual and tsk_vs_part is None:
      raise errors.BackEndError(
          'Missing TSK volume system part in non-virtual file entry.')

    super(TSKPartitionFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._name = None
    self._tsk_volume = tsk_volume
    self._tsk_vs_part = tsk_vs_part

    if is_virtual:
      self.entry_type = definitions.FILE_ENTRY_TYPE_DIRECTORY
    else:
      self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      TSKPartitionDirectory: a directory.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return None

    return tsk_partition_directory.TSKPartitionDirectory(
        self._file_system, self.path_spec)

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      TSKPartitionFileEntry: a sub file entry.
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield TSKPartitionFileEntry(
            self._resolver_context, self._file_system, path_spec)

  @property
  def name(self):
    """str: name of the file entry, which does not include the full path."""
    if self._name is None:
      # Directory entries without a location in the path specification
      # are not given a name for now.
      location = getattr(self.path_spec, 'location', None)
      if location is not None:
        self._name = self._file_system.BasenamePath(location)
      else:
        self._name = ''
    return self._name

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    if self._tsk_vs_part is None:
      return None

    number_of_sectors = tsk_partition.TSKVsPartGetNumberOfSectors(
        self._tsk_vs_part)
    if number_of_sectors is None:
      return None

    bytes_per_sector = tsk_partition.TSKVolumeGetBytesPerSector(
        self._tsk_volume)

    return number_of_sectors * bytes_per_sector

  # pylint: disable=redundant-returns-doc
  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      TSKPartitionFileEntry: parent file entry or None if not available.
    """
    # TODO: implement https://github.com/log2timeline/dfvfs/issues/76.
    return None

  def GetTSKVsPart(self):
    """Retrieves the TSK volume system part.

    Returns:
      pytsk3.TSK_VS_PART_INFO: a TSK volume system part or None if not
          available.
    """
    return self._tsk_vs_part

  def IsAllocated(self):
    """Determines if the file entry is allocated.

    Returns:
      bool: True if the file entry is allocated.
    """
    return self._is_virtual or tsk_partition.TSKVsPartIsAllocated(
        self._tsk_vs_part)
