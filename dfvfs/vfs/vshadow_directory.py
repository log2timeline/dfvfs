# -*- coding: utf-8 -*-
"""The Volume Shadow Snapshots (VSS) directory implementation."""

from dfvfs.path import vshadow_path_spec
from dfvfs.vfs import directory


class VShadowDirectory(directory.Directory):
  """File system directory that uses pyvshadow."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      VShadowPathSpec: a path specification.
    """
    location = getattr(self.path_spec, 'location', None)
    store_index = getattr(self.path_spec, 'store_index', None)

    # Only the virtual root file has directory entries.
    if (store_index is None and location is not None and
        location == self._file_system.LOCATION_ROOT):
      vshadow_volume = self._file_system.GetVShadowVolume()

      for store_index in range(0, vshadow_volume.number_of_stores):
        vss_store_index = store_index + 1
        yield vshadow_path_spec.VShadowPathSpec(
            location=f'/vss{vss_store_index:d}', parent=self.path_spec.parent,
            store_index=store_index)
