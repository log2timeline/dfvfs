# -*- coding: utf-8 -*-
"""The APFS container directory implementation."""

from dfvfs.path import apfs_container_path_spec
from dfvfs.vfs import directory


class APFSContainerDirectory(directory.Directory):
  """File system directory that uses pyfsapfs."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      APFSContainerPathSpec: a path specification.
    """
    # Only the virtual root file has directory entries.
    volume_index = self._file_system.GetVolumeIndexByPathSpec(self.path_spec)
    if volume_index is None:
      location = getattr(self.path_spec, 'location', None)
      if location and location == self._file_system.LOCATION_ROOT:
        fsapfs_container = self._file_system.GetAPFSContainer()

        for volume_index in range(0, fsapfs_container.number_of_volumes):
          apfs_volume_index = volume_index + 1
          apfs_volume_location = f'/apfs{apfs_volume_index:d}'
          yield apfs_container_path_spec.APFSContainerPathSpec(
              location=apfs_volume_location, parent=self.path_spec.parent,
              volume_index=volume_index)
