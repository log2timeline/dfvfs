# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) partition file entry implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import tsk_partition
from dfvfs.path import tsk_partition_path_spec
from dfvfs.vfs import file_entry
from dfvfs.vfs import vfs_stat


class TSKPartitionDirectory(file_entry.Directory):
  """Class that implements a directory object using pytsk3."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      A path specification (instance of path.TSKPartitionPathSpec).
    """
    # Only the virtual root file has directory entries.
    part_index = getattr(self.path_spec, u'part_index', None)
    start_offset = getattr(self.path_spec, u'start_offset', None)

    if part_index is not None or start_offset is not None:
      return

    location = getattr(self.path_spec, u'location', None)
    if location is None or location != self._file_system.LOCATION_ROOT:
      return

    tsk_volume = self._file_system.GetTSKVolume()
    bytes_per_sector = tsk_partition.TSKVolumeGetBytesPerSector(tsk_volume)
    part_index = 0
    partition_index = 0

    # pytsk3 does not handle the Volume_Info iterator correctly therefore
    # the explicit list is needed to prevent the iterator terminating too
    # soon or looping forever.
    for tsk_vs_part in list(tsk_volume):
      kwargs = {}

      if tsk_partition.TSKVsPartIsAllocated(tsk_vs_part):
        partition_index += 1
        kwargs[u'location'] = u'/p{0:d}'.format(partition_index)

      kwargs[u'part_index'] = part_index
      part_index += 1

      start_sector = tsk_partition.TSKVsPartGetStartSector(tsk_vs_part)

      if start_sector is not None:
        kwargs[u'start_offset'] = start_sector * bytes_per_sector

      kwargs[u'parent'] = self.path_spec.parent

      yield tsk_partition_path_spec.TSKPartitionPathSpec(**kwargs)


class TSKPartitionFileEntry(file_entry.FileEntry):
  """Class that implements a file entry object using pytsk3."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK_PARTITION

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False):
    """Initializes the file entry object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      file_system: the file system object (instance of FileSystem).
      path_spec: the path specification (instance of PathSpec).
      is_virtual: optional boolean value to indicate if the file entry is
                  a virtual file entry emulated by the corresponding file
                  system.
    """
    super(TSKPartitionFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._name = None

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      A directory object (instance of Directory) or None.
    """
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if (self._stat_object and
        self._stat_object.type == self._stat_object.TYPE_DIRECTORY):
      return TSKPartitionDirectory(self._file_system, self.path_spec)
    return

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of vfs.VFSStat).

    Raises:
      BackEndError: when the tsk volume system part is missing in a non-virtual
                    file entry.
    """
    tsk_vs_part = self.GetTSKVsPart()
    stat_object = vfs_stat.VFSStat()

    if not self._is_virtual and tsk_vs_part is None:
      raise errors.BackEndError(
          u'Missing tsk volume system part in non-virtual file entry.')

    tsk_volume = self._file_system.GetTSKVolume()
    bytes_per_sector = tsk_partition.TSKVolumeGetBytesPerSector(tsk_volume)

    # File data stat information.
    if tsk_vs_part is not None:
      number_of_sectors = tsk_partition.TSKVsPartGetNumberOfSectors(
          tsk_vs_part)

      if number_of_sectors:
        stat_object.size = number_of_sectors * bytes_per_sector

    # Date and time stat information.

    # Ownership and permissions stat information.

    # File entry type stat information.

    # The root file entry is virtual and should have type directory.
    if self._is_virtual:
      stat_object.type = stat_object.TYPE_DIRECTORY
    else:
      stat_object.type = stat_object.TYPE_FILE

    if not self._is_virtual:
      stat_object.is_allocated = tsk_partition.TSKVsPartIsAllocated(
          tsk_vs_part)

    return stat_object

  @property
  def name(self):
    """The name of the file entry, which does not include the full path."""
    if self._name is None:
      # Directory entries without a location in the path specification
      # are not given a name for now.
      location = getattr(self.path_spec, u'location', None)
      if location is not None:
        self._name = self._file_system.BasenamePath(location)
      else:
        self._name = u''
    return self._name

  @property
  def sub_file_entries(self):
    """The sub file entries (generator of instance of vfs.FileEntry)."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield TSKPartitionFileEntry(
            self._resolver_context, self._file_system, path_spec)

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      The parent file entry (instance of FileEntry) or None.
    """
    # TODO: implement https://github.com/log2timeline/dfvfs/issues/76.
    return

  def GetTSKVsPart(self):
    """Retrieves the TSK volume system part object.

    Returns:
      A TSK volume system part object (instance of pytsk3.TSK_VS_PART_INFO)
      or None.
    """
    tsk_volume = self._file_system.GetTSKVolume()
    tsk_vs_part, _ = tsk_partition.GetTSKVsPartByPathSpec(
        tsk_volume, self.path_spec)
    return tsk_vs_part
