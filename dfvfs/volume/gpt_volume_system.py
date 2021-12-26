# -*- coding: utf-8 -*-
"""The GUID Partition Table (GPT) volume system."""

from dfvfs.lib import definitions
from dfvfs.volume import factory
from dfvfs.volume import volume_system


class GPTVolume(volume_system.Volume):
  """Volume that uses pyvsgpt."""

  def __init__(self, file_entry):
    """Initializes a GPT volume.

    Args:
      file_entry (GPTFileEntry): a GPT file entry.
    """
    super(GPTVolume, self).__init__(file_entry.name)
    self._file_entry = file_entry

  def _Parse(self):
    """Extracts attributes and extents from the volume."""
    vsgpt_partition = self._file_entry.GetGPTPartition()

    volume_attribute = volume_system.VolumeAttribute(
        'identifier', vsgpt_partition.identifier)
    self._AddAttribute(volume_attribute)

    volume_extent = volume_system.VolumeExtent(
        vsgpt_partition.volume_offset, vsgpt_partition.size)
    self._extents.append(volume_extent)


class GPTVolumeSystem(volume_system.VolumeSystem):
  """Volume system that uses pyvsgpt."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_GPT

  VOLUME_IDENTIFIER_PREFIX = 'p'

  def _Parse(self):
    """Extracts sections and volumes from the volume system."""
    root_file_entry = self._file_system.GetRootFileEntry()

    for sub_file_entry in root_file_entry.sub_file_entries:
      volume = GPTVolume(sub_file_entry)
      self._AddVolume(volume)


factory.Factory.RegisterVolumeSystem(GPTVolumeSystem)
