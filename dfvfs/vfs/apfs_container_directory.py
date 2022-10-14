# -*- coding: utf-8 -*-
"""The APFS container directory implementation."""

from dfvfs.lib import apfs_helper
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
    volume_index = apfs_helper.APFSContainerPathSpecGetVolumeIndex(
        self.path_spec)
    if volume_index is not None:
      return

    location = getattr(self.path_spec, 'location', None)
    if location is None or location != self._file_system.LOCATION_ROOT:
      return

    fsapfs_container = self._file_system.GetAPFSContainer()

    for volume_index in range(0, fsapfs_container.number_of_volumes):
      apfs_volume_index = volume_index + 1
      yield apfs_container_path_spec.APFSContainerPathSpec(
          location=f'/apfs{apfs_volume_index:d}', parent=self.path_spec.parent,
          volume_index=volume_index)
