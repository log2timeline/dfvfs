# -*- coding: utf-8 -*-
"""Volume system object implementation using the SleuthKit (TSK)."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import tsk_partition
from dfvfs.resolver import resolver
from dfvfs.volume import volume_system


class TSKVolume(volume_system.Volume):
  """Class that implements a volume object using pytsk3."""

  def __init__(self, file_entry, bytes_per_sector):
    """Initializes the volume object.

    Args:
      file_entry: a TSK partition file entry object (instance of FileEntry).
      bytes_per_sector: an integer containing number of bytes per sector.
    """
    super(TSKVolume, self).__init__(file_entry.name)
    self._file_entry = file_entry
    self._bytes_per_sector = bytes_per_sector

  def _Parse(self):
    """Extracts attributes and extents from the volume."""
    tsk_vs_part = self._file_entry.GetTSKVsPart()

    tsk_addr = getattr(tsk_vs_part, u'addr', None)
    if tsk_addr is not None:
      self._AddAttribute(volume_system.VolumeAttribute(u'address', tsk_addr))

    tsk_desc = getattr(tsk_vs_part, u'desc', None)
    if tsk_desc is not None:
      # pytsk3 returns an UTF-8 encoded byte string.
      try:
        tsk_desc = tsk_desc.decode(u'utf8')
        self._AddAttribute(volume_system.VolumeAttribute(
            u'description', tsk_desc))
      except UnicodeError:
        pass

    start_sector = tsk_partition.TSKVsPartGetStartSector(tsk_vs_part)
    number_of_sectors = tsk_partition.TSKVsPartGetNumberOfSectors(tsk_vs_part)
    volume_extent = volume_system.VolumeExtent(
        start_sector * self._bytes_per_sector,
        number_of_sectors * self._bytes_per_sector)
    self._extents.append(volume_extent)


class TSKVolumeSystem(volume_system.VolumeSystem):
  """Class that implements a volume system object using pytsk3."""

  def __init__(self):
    """Initializes the volume system object.

    Raises:
      VolumeSystemError: if the volume system could not be accessed.
    """
    super(TSKVolumeSystem, self).__init__()
    self._file_system = None
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

  def Open(self, path_spec):
    """Opens a volume object defined by path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).

    Raises:
      VolumeSystemError: if the TSK partition virtual file system could not
                         be resolved.
    """
    self._file_system = resolver.Resolver.OpenFileSystem(path_spec)
    if self._file_system is None:
      raise errors.VolumeSystemError(
          u'Unable to resolve file system from path specification.')

    type_indicator = self._file_system.type_indicator
    if type_indicator != definitions.TYPE_INDICATOR_TSK_PARTITION:
      raise errors.VolumeSystemError(u'Unsupported file system type.')
