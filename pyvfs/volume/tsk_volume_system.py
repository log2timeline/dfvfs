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
"""Volume system object implementation using the SleuthKit (TSK)."""

import pytsk3

from pyvfs.lib import errors
from pyvfs.volume import volume_system


class TSKVolume(volume_system.Volume):
  """Class that implements a volume object using the SleuthKit."""

  def __init__(self, tsk_vs_part):
    """Initializes the volume object.

    Args:
      tsk_vs_part: a SleuthKit volume systme part object (TSK_VS_PART_INFO).
    """
    super(TSKVolume, self).__init__()
    self._tsk_vs_part = tsk_vs_part

  @property
  def address(self):
    """The address (volume system part index)."""
    return self._tsk_vs_part.addr

  @property
  def description(self):
    """The description."""
    return self._tsk_vs_part.desc


class TSKVolumeSystem(volume_system.VolumeSystem):
  """Class that implements a volume system object using the SleuthKit."""

  def __init__(self, tsk_image):
    """Initializes the SleuthKit volume system object.

    Args:
      tsk_image: a SleuthKit image object (pytsk3.Img_Info).

    Raises:
      VolumeSystemError: if the volume system could not be accessed.
    """
    super(TSKVolumeSystem, self).__init__()
    self._tsk_image = tsk_image

    try:
      self._tsk_volume = pytsk3.Volume_Info(tsk_image)
    except IOError as exception:
      raise errors.VolumeSystemError(
          u'Unable to access volume system with error: %s.' % exception)

    self.block_size = getattr(self._tsk_volume.info, 'block_size', 512)

  def _Parse(self):
    """Extracts sections and volumes from the volume system."""
    # Sticking with the SleuthKit naming convention here, ts_vs_part is
    # a volume system section (part) and tsk_volume is the volume system.
    for ts_vs_part in self._tsk_volume:
      volume_extent = volume_system.VolumeExtent(
          ts_vs_part.start * self.block_size,
          ts_vs_part.len * self.block_size)

      self._sections.append(volume_extent)

      if ts_vs_part.flags == pytsk3.TSK_VS_PART_FLAG_ALLOC:
        volume = TSKVolume(ts_vs_part)
        volume.AddExtent(volume_extent)

        self._volumes.append(volume)
