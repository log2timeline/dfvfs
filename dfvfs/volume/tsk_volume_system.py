# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) volume system."""

from dfvfs.lib import definitions
from dfvfs.lib import tsk_partition
from dfvfs.volume import factory
from dfvfs.volume import volume_system


class TSKVolume(volume_system.Volume):
  """Volume that uses pytsk3."""

  def __init__(self, file_entry, bytes_per_sector):
    """Initializes a volume.

    Args:
      file_entry (TSKPartitionFileEntry): a TSK partition file entry.
      bytes_per_sector (int): number of bytes per sector.
    """
    super(TSKVolume, self).__init__(file_entry.name)
    self._file_entry = file_entry
    self._bytes_per_sector = bytes_per_sector

  def _Parse(self):
    """Extracts attributes and extents from the volume."""
    tsk_vs_part = self._file_entry.GetTSKVsPart()

    tsk_addr = getattr(tsk_vs_part, 'addr', None)
    if tsk_addr is not None:
      address = volume_system.VolumeAttribute('address', tsk_addr)
      self._AddAttribute(address)

    tsk_desc = getattr(tsk_vs_part, 'desc', None)
    if tsk_desc is not None:
      # pytsk3 returns an UTF-8 encoded byte string.
      try:
        tsk_desc = tsk_desc.decode('utf8')
        self._AddAttribute(volume_system.VolumeAttribute(
            'description', tsk_desc))
      except UnicodeError:
        pass

    start_sector = tsk_partition.TSKVsPartGetStartSector(tsk_vs_part)
    number_of_sectors = tsk_partition.TSKVsPartGetNumberOfSectors(tsk_vs_part)
    volume_extent = volume_system.VolumeExtent(
        start_sector * self._bytes_per_sector,
        number_of_sectors * self._bytes_per_sector)
    self._extents.append(volume_extent)


class TSKVolumeSystem(volume_system.VolumeSystem):
  """Volume system that uses pytsk3."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK_PARTITION

  VOLUME_IDENTIFIER_PREFIX = 'p'

  def __init__(self):
    """Initializes a volume system.

    Raises:
      VolumeSystemError: if the volume system could not be accessed.
    """
    super(TSKVolumeSystem, self).__init__()
    self.bytes_per_sector = 512

  def _Parse(self):
    """Extracts sections and volumes from the volume system."""
    root_file_entry = self._file_system.GetRootFileEntry()
    tsk_volume = self._file_system.GetTSKVolume()
    self.bytes_per_sector = tsk_partition.TSKVolumeGetBytesPerSector(tsk_volume)

    for sub_file_entry in root_file_entry.sub_file_entries:
      tsk_vs_part = sub_file_entry.GetTSKVsPart()
      start_sector = tsk_partition.TSKVsPartGetStartSector(tsk_vs_part)
      number_of_sectors = tsk_partition.TSKVsPartGetNumberOfSectors(tsk_vs_part)

      if start_sector is None or number_of_sectors is None:
        continue

      if tsk_partition.TSKVsPartIsAllocated(tsk_vs_part):
        volume = TSKVolume(sub_file_entry, self.bytes_per_sector)
        self._AddVolume(volume)

      volume_extent = volume_system.VolumeExtent(
          start_sector * self.bytes_per_sector,
          number_of_sectors * self.bytes_per_sector)

      self._sections.append(volume_extent)


factory.Factory.RegisterVolumeSystem(TSKVolumeSystem)
