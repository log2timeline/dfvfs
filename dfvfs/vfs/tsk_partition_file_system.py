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
"""The SleuthKit (TSK) partition file system implementation."""

# This is necessary to prevent a circular import.
import dfvfs.vfs.tsk_partition_file_entry

from dfvfs.lib import definitions
from dfvfs.lib import tsk_partition
from dfvfs.path import tsk_partition_path_spec
from dfvfs.vfs import file_system


class TSKPartitionFileSystem(file_system.FileSystem):
  """Class that implements a file system object using pytsk3."""

  LOCATION_ROOT = u'/'
  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK_PARTITION

  def __init__(self, tsk_volume, path_spec):
    """Initializes the file system object.

    Args:
      tsk_volume: the TSK volume object (instance of pytsk.Volume_Info).
      path_spec: the path specification (instance of path.PathSpec) of
                 the file-like object.
    """
    super(TSKPartitionFileSystem, self).__init__()
    self._tsk_volume = tsk_volume
    self._path_spec = path_spec

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      Boolean indicating if the file entry exists.
    """
    tsk_vs_part, _ = tsk_partition.GetTSKVsPartByPathSpec(
        self._tsk_volume, path_spec)

    # The virtual root file has not corresponding TSK volume system part object
    # but should have a location.
    if tsk_vs_part is None:
      location = getattr(path_spec, 'location', None)
      return location is not None and location == self.LOCATION_ROOT

    return True

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A file entry (instance of vfs.TSKPartitionFileEntry) or None.
    """
    tsk_vs_part, partition_index = tsk_partition.GetTSKVsPartByPathSpec(
        self._tsk_volume, path_spec)

    location = getattr(path_spec, 'location', None)

    # The virtual root file has not corresponding TSK volume system part object
    # but should have a location.
    if tsk_vs_part is None:
      if location is None or location != self.LOCATION_ROOT:
        return
      return self.GetRootFileEntry()

    if location is None and partition_index is not None:
      path_spec.location = u'/p{0:d}'.format(partition_index)

    return dfvfs.vfs.tsk_partition_file_entry.TSKPartitionFileEntry(
        self, path_spec)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry).
    """
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=self.LOCATION_ROOT, parent=self._path_spec)
    return dfvfs.vfs.tsk_partition_file_entry.TSKPartitionFileEntry(
        self, path_spec)

  def GetTSKVolume(self):
    """Retrieves the TSK volume object.

    Returns:
      The TSK volume object (instance of pytsk3.Volume_Info).
    """
    return self._tsk_volume
