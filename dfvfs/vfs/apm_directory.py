# -*- coding: utf-8 -*-
"""The Apple Partition Map (APM) directory implementation."""

from dfvfs.path import apm_path_spec
from dfvfs.vfs import directory


class APMDirectory(directory.Directory):
  """File system directory that uses pyvsapm."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      APMPathSpec: a path specification.
    """
    entry_index = getattr(self.path_spec, 'entry_index', None)
    location = getattr(self.path_spec, 'location', None)

    # Only the virtual root file has directory entries.
    if (entry_index is None and location is not None and
        location == self._file_system.LOCATION_ROOT):
      vsapm_volume = self._file_system.GetAPMVolume()

      for partition_index in range(vsapm_volume.number_of_partitions):
        apm_entry_index = partition_index + 1
        yield apm_path_spec.APMPathSpec(
            entry_index=entry_index, location=f'/p{apm_entry_index:d}',
            parent=self.path_spec.parent)
