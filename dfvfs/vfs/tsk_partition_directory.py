# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) partition directory implementation."""

import pytsk3

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
          partition_number = None

          tsk_vs_info = getattr(tsk_vs_part, 'vs', None)
          if getattr(tsk_vs_info, 'vstype', None) == pytsk3.TSK_VS_TYPE_DOS:
            tsk_slot_num = getattr(tsk_vs_part, 'slot_num', -1)
            tsk_table_num = getattr(tsk_vs_part, 'table_num', -1)

            if tsk_slot_num >= 0 and tsk_table_num >= 0:
              partition_number = (tsk_table_num * 4) + tsk_slot_num + 1

          partition_index += 1
          if partition_number is None:
            partition_number = partition_index

          kwargs['location'] = f'/p{partition_number:d}'

        kwargs['part_index'] = part_index
        part_index += 1

        start_sector = tsk_partition.TSKVsPartGetStartSector(tsk_vs_part)

        if start_sector is not None:
          kwargs['start_offset'] = start_sector * bytes_per_sector

        kwargs['parent'] = self.path_spec.parent

        yield tsk_partition_path_spec.TSKPartitionPathSpec(**kwargs)
