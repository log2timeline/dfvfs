#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The PyVFS Project Authors.
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
"""Volume system object implementation using Volume Shadow Snapshots (VSS)."""

import pyvshadow

from pyvfs.lib import errors
from pyvfs.volume import volume_system


class VShadowVolume(volume_system.Volume):
  """Class that implements a volume object using VSS."""

  def __init__(self, vshadow_store, store_index):
    """Initializes the volume object.

    Args:
      vshadow_store: the VSS store object (pyvshadow.store).
      store_index: the VSS store index.
    """
    super(VShadowVolume, self).__init__()
    self._vshadow_store = vshadow_store
    self._store_index = store_index


class VShadowVolumeSystem(volume_system.VolumeSystem):
  """Class that implements a volume system object using VSS."""

  def __init__(self, file_object):
    """Initializes the VSS volume system object.

    Args:
      file_object: a file-like object containing the VSS volume.

    Raises:
      VolumeSystemError: if the volume system could not be accessed.
    """
    super(VShadowVolumeSystem, self).__init__()
    self._vshadow_volume = pyvshadow.volume()

    self._file_object = file_object
    try:
      self._vshadow_volume.open_file_object(file_object)
    except IOError as exception:
      raise errors.VolumeSystemError(
          u'Unable to access volume system with error: {0:s}.'.format(
              exception))

  def _Parse(self):
    """Extracts sections and volumes from the volume system."""
    store_index = 0
    for vshadow_store in self._vshadow_volume.stores:
      volume_extent = volume_system.VolumeExtent(
          0, vshadow_store.volume_size)
      volume = VShadowVolume(vshadow_store, store_index)

      volume.AddExtent(volume_extent)
      self._volumes.append(volume)

      store_index += 1

    volume = volume_system.Volume()
    volume_extent = volume_system.VolumeExtent(
        0, self._file_object.get_size())

    volume.AddExtent(volume_extent)
    self._volumes.append(volume)
