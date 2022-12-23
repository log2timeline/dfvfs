# -*- coding: utf-8 -*-
"""The Core Storage (CS) volume system."""

from dfvfs.lib import definitions
from dfvfs.volume import factory
from dfvfs.volume import volume_system


class CSVolume(volume_system.Volume):
  """Volume that uses pyfvde."""

  def __init__(self, file_entry):
    """Initializes a CS volume.

    Args:
      file_entry (CSFileEntry): a CS file entry.
    """
    super(CSVolume, self).__init__(file_entry.name)
    self._file_entry = file_entry

  def _Parse(self):
    """Extracts attributes and extents from the volume."""
    fvde_logical_volume = self._file_entry.GetFVDELogicalVolume()

    volume_attribute = volume_system.VolumeAttribute(
        'identifier', fvde_logical_volume.identifier)
    self._AddAttribute(volume_attribute)

    # TODO: implement in pyfvde
    # TODO: add support for creation time
    # TODO: add support for logical volume extents
    volume_extent = volume_system.VolumeExtent(0, fvde_logical_volume.size)
    self._extents.append(volume_extent)


class CSVolumeSystem(volume_system.VolumeSystem):
  """Volume system that uses pyfvde."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_CS

  VOLUME_IDENTIFIER_PREFIX = 'cs'

  def _Parse(self):
    """Extracts sections and volumes from the volume system."""
    root_file_entry = self._file_system.GetRootFileEntry()

    for sub_file_entry in root_file_entry.sub_file_entries:
      volume = CSVolume(sub_file_entry)
      self._AddVolume(volume)


factory.Factory.RegisterVolumeSystem(CSVolumeSystem)
