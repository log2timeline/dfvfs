# -*- coding: utf-8 -*-
"""The Apple Partition Map (APM) volume system."""

from dfvfs.lib import definitions
from dfvfs.volume import factory
from dfvfs.volume import volume_system


class APMVolume(volume_system.Volume):
  """Volume that uses pyvsapm."""

  def __init__(self, file_entry):
    """Initializes a APM volume.

    Args:
      file_entry (APMFileEntry): a APM file entry.
    """
    super(APMVolume, self).__init__(file_entry.name)
    self._file_entry = file_entry

  def _Parse(self):
    """Extracts attributes and extents from the volume."""
    vsapm_partition = self._file_entry.GetAPMPartition()

    volume_attribute = volume_system.VolumeAttribute(
        'name', vsapm_partition.name_string)
    self._AddAttribute(volume_attribute)

    volume_extent = volume_system.VolumeExtent(
        vsapm_partition.volume_offset, vsapm_partition.size)
    self._extents.append(volume_extent)


class APMVolumeSystem(volume_system.VolumeSystem):
  """Volume system that uses pyvsapm."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_APM

  VOLUME_IDENTIFIER_PREFIX = 'p'

  def _Parse(self):
    """Extracts sections and volumes from the volume system."""
    root_file_entry = self._file_system.GetRootFileEntry()

    for sub_file_entry in root_file_entry.sub_file_entries:
      volume = APMVolume(sub_file_entry)
      self._AddVolume(volume)


factory.Factory.RegisterVolumeSystem(APMVolumeSystem)
