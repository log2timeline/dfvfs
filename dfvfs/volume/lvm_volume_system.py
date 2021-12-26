# -*- coding: utf-8 -*-
"""The Logical Volume Manager (LVM) volume system."""

from dfvfs.lib import definitions
from dfvfs.volume import factory
from dfvfs.volume import volume_system


class LVMVolume(volume_system.Volume):
  """Volume that uses pyvslvm."""

  def __init__(self, file_entry):
    """Initializes a LVM volume.

    Args:
      file_entry (LVMFileEntry): a LVM file entry.
    """
    super(LVMVolume, self).__init__(file_entry.name)
    self._file_entry = file_entry

  def _Parse(self):
    """Extracts attributes and extents from the volume."""
    vslvm_logical_volume = self._file_entry.GetLVMLogicalVolume()

    volume_attribute = volume_system.VolumeAttribute(
        'identifier', vslvm_logical_volume.identifier)
    self._AddAttribute(volume_attribute)

    # TODO: implement in pyvslvm
    # TODO: add support for creation time
    # TODO: add support for logical volume extents
    volume_extent = volume_system.VolumeExtent(0, vslvm_logical_volume.size)
    self._extents.append(volume_extent)


class LVMVolumeSystem(volume_system.VolumeSystem):
  """Volume system that uses pyvslvm."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_LVM

  VOLUME_IDENTIFIER_PREFIX = 'lvm'

  def _Parse(self):
    """Extracts sections and volumes from the volume system."""
    root_file_entry = self._file_system.GetRootFileEntry()

    for sub_file_entry in root_file_entry.sub_file_entries:
      volume = LVMVolume(sub_file_entry)
      self._AddVolume(volume)


factory.Factory.RegisterVolumeSystem(LVMVolumeSystem)
