# -*- coding: utf-8 -*-
"""The Volume Shadow Snapshots (VSS) volume system."""

from dfvfs.lib import definitions
from dfvfs.volume import factory
from dfvfs.volume import volume_system


class VShadowVolume(volume_system.Volume):
  """Volume that uses pyvshadow."""

  def __init__(self, file_entry):
    """Initializes a volume.

    Args:
      file_entry (VShadowFileEntry): a VSS file entry.
    """
    super(VShadowVolume, self).__init__(file_entry.name)
    self._file_entry = file_entry

  def _Parse(self):
    """Extracts attributes and extents from the volume."""
    vshadow_store = self._file_entry.GetVShadowStore()

    self._AddAttribute(volume_system.VolumeAttribute(
        'identifier', vshadow_store.identifier))
    self._AddAttribute(volume_system.VolumeAttribute(
        'copy_identifier', vshadow_store.copy_identifier))
    self._AddAttribute(volume_system.VolumeAttribute(
        'copy_set_identifier', vshadow_store.copy_set_identifier))
    self._AddAttribute(volume_system.VolumeAttribute(
        'creation_time', vshadow_store.get_creation_time_as_integer()))

    volume_extent = volume_system.VolumeExtent(0, vshadow_store.volume_size)
    self._extents.append(volume_extent)

  def HasExternalData(self):
    """Determines if the volume has external stored data.

    Returns:
      bool: True if the volume has external stored data.
    """
    vshadow_store = self._file_entry.GetVShadowStore()

    return not vshadow_store.has_in_volume_data()


class VShadowVolumeSystem(volume_system.VolumeSystem):
  """Volume system that uses pyvshadow."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VSHADOW

  VOLUME_IDENTIFIER_PREFIX = 'vss'

  def _Parse(self):
    """Extracts sections and volumes from the volume system."""
    root_file_entry = self._file_system.GetRootFileEntry()

    for sub_file_entry in root_file_entry.sub_file_entries:
      volume = VShadowVolume(sub_file_entry)
      self._AddVolume(volume)


factory.Factory.RegisterVolumeSystem(VShadowVolumeSystem)
