# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) partition directory implementation."""

from dfvfs.lib import tsk_partition
from dfvfs.path import tsk_partition_path_spec
from dfvfs.vfs import directory


class TSKPartitionDirectory(directory.Directory):
  """File system directory that uses pytsk3."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      TSKPartitionPathSpec: a path specification.
    """
    location = getattr(self.path_spec, 'location', None)
    part_index = getattr(self.path_spec, 'part_index', None)
    start_offset = getattr(self.path_spec, 'start_offset', None)

    # Only the virtual root file has directory entries.
    if (part_index is None and start_offset is None and
        location is not None and location == self._file_system.LOCATION_ROOT):
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
          kwargs['location'] = f'/p{partition_index:d}'

        kwargs['part_index'] = part_index
        part_index += 1

        start_sector = tsk_partition.TSKVsPartGetStartSector(tsk_vs_part)

        if start_sector is not None:
          kwargs['start_offset'] = start_sector * bytes_per_sector

        kwargs['parent'] = self.path_spec.parent

        yield tsk_partition_path_spec.TSKPartitionPathSpec(**kwargs)
