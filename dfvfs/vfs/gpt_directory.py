# -*- coding: utf-8 -*-
"""The GUID Partition Table (GPT) directory implementation."""

from dfvfs.path import gpt_path_spec
from dfvfs.vfs import directory


class GPTDirectory(directory.Directory):
  """File system directory that uses pyvsgpt."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      GPTPathSpec: a path specification.
    """
    entry_index = getattr(self.path_spec, 'entry_index', None)
    location = getattr(self.path_spec, 'location', None)

    # Only the virtual root file has directory entries.
    if (entry_index is None and location is not None and
        location == self._file_system.LOCATION_ROOT):
      vsgpt_volume = self._file_system.GetGPTVolume()

      for partition in vsgpt_volume.partitions:
        gpt_entry_index = partition.entry_index + 1
        yield gpt_path_spec.GPTPathSpec(
            entry_index=entry_index, location=f'/p{gpt_entry_index:d}',
            parent=self.path_spec.parent)
