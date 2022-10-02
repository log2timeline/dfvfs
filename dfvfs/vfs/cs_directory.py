# -*- coding: utf-8 -*-
"""The Core Storage (CS) directory implementation."""

from dfvfs.path import cs_path_spec
from dfvfs.vfs import directory


class CSDirectory(directory.Directory):
  """File system directory that uses pyfvde."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      CSPathSpec: a path specification.
    """
    volume_index = getattr(self.path_spec, 'volume_index', None)
    location = getattr(self.path_spec, 'location', None)

    # Only the virtual root file has directory entries.
    if (volume_index is None and location is not None and
        location == self._file_system.LOCATION_ROOT):
      fvde_volume_group = self._file_system.GetFVDEVolumeGroup()

      for volume_index in range(fvde_volume_group.number_of_logical_volumes):
        fvde_volume_index = volume_index + 1
        yield cs_path_spec.CSPathSpec(
            location=f'/cs{fvde_volume_index:d}', parent=self.path_spec.parent,
            volume_index=volume_index)
