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
"""The SleuthKit (TSK) partition file-like object implementation."""

# This is necessary to prevent a circular import.
import dfvfs.vfs.manager

from dfvfs.file_io import data_range_io
from dfvfs.lib import errors
from dfvfs.lib import tsk_partition
from dfvfs.resolver import resolver


class TSKPartitionFile(data_range_io.DataRange):
  """Class that implements a file-like object using pytsk3."""

  def __init__(self, tsk_volume=None, tsk_vs_part=None):
    """Initializes the file-like object.

    Args:
      tsk_volume: optional SleuthKit volume object (instance of
                  pytsk3.Volume_Info). The default is None.
      tsk_vs_part: optional SleuthKit file object (instance of
                   pytsk3.TSK_VS_PART_INFO). The default is None.

    Raises:
      ValueError: if tsk_vs_part provided but tsk_volume is not.
    """
    if tsk_vs_part is not None and tsk_volume is None:
      raise ValueError(
          u'TSK volume system part object provided without corresponding '
          u'volume object.')

    super(TSKPartitionFile, self).__init__()
    self._tsk_volume = tsk_volume
    self._tsk_vs_part = tsk_vs_part

    if tsk_vs_part:
      self._tsk_vs_part_set_in_init = True
    else:
      self._tsk_vs_part_set_in_init = False

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.

  def open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: optional path specification (instance of path.PathSpec).
                 The default is None.
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      IOError: if the open file-like object could not be opened.
      ValueError: if the path specification or mode is invalid.
    """
    if not path_spec:
      raise ValueError(u'Missing path specfication.')

    if not self._tsk_vs_part_set_in_init:
      if not path_spec.HasParent():
        raise errors.PathSpecError(
            u'Unsupported path specification without parent.')

      file_system = dfvfs.vfs.manager.FileSystemManager.OpenFileSystem(
          path_spec)
      self._tsk_volume = file_system.GetTSKVolume()
      self._tsk_vs, _ = tsk_partition.GetTSKVsPartByPathSpec(
          self._tsk_volume, path_spec)

      if self._tsk_vs is None:
        raise errors.PathSpecError(
            u'Unable to retrieve TSK volume system part from path '
            u'specification.')

      range_offset = tsk_partition.TSKVsPartGetStartSector(self._tsk_vs)
      range_size = tsk_partition.TSKVsPartGetNumberOfSectors(self._tsk_vs)

      if range_offset is None or range_size is None:
        raise errors.PathSpecError(
            u'Unable to retrieve TSK volume system part data range from path '
            u'specification.')

      bytes_per_sector = tsk_partition.TSKVolumeGetBytesPerSector(
          self._tsk_volume)
      range_offset *= bytes_per_sector
      range_size *= bytes_per_sector

      self.SetRange(range_offset, range_size)
      self._file_object = resolver.Resolver.OpenFileObject(path_spec.parent)
      self._file_object_set_in_init = True

    super(TSKPartitionFile, self).open(path_spec, mode=mode)
