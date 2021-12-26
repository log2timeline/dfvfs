# -*- coding: utf-8 -*-
"""The Apple File System (APFS) volume system."""

from dfvfs.lib import definitions
from dfvfs.volume import factory
from dfvfs.volume import volume_system


class APFSVolume(volume_system.Volume):
  """Volume that uses pyfsapfs."""

  def __init__(self, file_entry):
    """Initializes an APFS volume.

    Args:
      file_entry (APFSContainerFileEntry): an APFS container file entry.
    """
    super(APFSVolume, self).__init__(file_entry.name)
    self._file_entry = file_entry

  def _Parse(self):
    """Extracts attributes and extents from the volume."""
    fsapfs_volume = self._file_entry.GetAPFSVolume()

    volume_attribute = volume_system.VolumeAttribute(
        'identifier', fsapfs_volume.identifier)
    self._AddAttribute(volume_attribute)

    volume_attribute = volume_system.VolumeAttribute(
        'name', fsapfs_volume.name)
    self._AddAttribute(volume_attribute)

    # TODO: implement in pyfsapfs
    # TODO: add support for creation time
    # TODO: add support for volume size


class APFSVolumeSystem(volume_system.VolumeSystem):
  """Volume system that uses pyfsapfs."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_APFS_CONTAINER

  VOLUME_IDENTIFIER_PREFIX = 'apfs'

  def _Parse(self):
    """Extracts sections and volumes from the volume system."""
    root_file_entry = self._file_system.GetRootFileEntry()

    for sub_file_entry in root_file_entry.sub_file_entries:
      volume = APFSVolume(sub_file_entry)
      self._AddVolume(volume)


factory.Factory.RegisterVolumeSystem(APFSVolumeSystem)
