# -*- coding: utf-8 -*-
"""The Logical Volume Manager (LVM) directory implementation."""

from dfvfs.path import lvm_path_spec
from dfvfs.vfs import directory


class LVMDirectory(directory.Directory):
  """File system directory that uses pyvslvm."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      LVMPathSpec: a path specification.
    """
    volume_index = getattr(self.path_spec, 'volume_index', None)
    location = getattr(self.path_spec, 'location', None)

    # Only the virtual root file has directory entries.
    if (volume_index is None and location is not None and
        location == self._file_system.LOCATION_ROOT):
      vslvm_volume_group = self._file_system.GetLVMVolumeGroup()

      for volume_index in range(vslvm_volume_group.number_of_logical_volumes):
        lvm_volume_index = volume_index + 1
        yield lvm_path_spec.LVMPathSpec(
            location=f'/lvm{lvm_volume_index:d}', parent=self.path_spec.parent,
            volume_index=volume_index)
