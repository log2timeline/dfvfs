#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The dfVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
      file_entry: the TSK partition file entry object (instance of
                  vfs.TSKPartitionFileEntry).
      bytes_per_sector: the number of bytes per sector.
    """
    super(TSKVolume, self).__init__(file_entry.name)
    self._file_entry = file_entry
    self._bytes_per_sector = bytes_per_sector

  def _Parse(self):
    """Extracts attributes and extents from the volume."""
    tsk_vs_part = self._file_entry.GetTSKVsPart()

    tsk_addr = getattr(tsk_vs_part, 'addr', None)
    if tsk_addr is not None:
      self._AddAttribute(volume_system.VolumeAttribute('address', tsk_addr))

    tsk_desc = getattr(tsk_vs_part, 'desc', None)
    if tsk_desc is not None:
      self._AddAttribute(volume_system.VolumeAttribute('description', tsk_desc))

    start_sector = tsk_partition.TSKVsPartGetStartSector(tsk_vs_part)
    number_of_sectors = tsk_partition.TSKVsPartGetNumberOfSectors(tsk_vs_part)
    self._extents.append(volume_system.VolumeExtent(
        start_sector * self._bytes_per_sector,
        number_of_sectors * self._bytes_per_sector))


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
      path_spec: the VFS path specification (instance of path.PathSpec).

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
