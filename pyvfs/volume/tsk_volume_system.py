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
  """Class that implements a volume object using pytsk3."""

  def __init__(self, tsk_vs_part, volume_index, block_size):
    """Initializes the volume object.

    Args:
      tsk_vs_part: a SleuthKit volume system part object (instance of
                   pytsk3.TSK_VS_PART_INFO).
      volume_index: the volume index number.
      block_size: the block (or sector) size used by SleuthKit.
    """
    identifier = u'p{0:d}'.format(volume_index + 1)
    super(TSKVolume, self).__init__(identifier)
    self._tsk_vs_part = tsk_vs_part
    self._block_size = block_size

  def _Parse(self):
    """Extracts attributes and extents from the volume."""
    tsk_addr = getattr(self._tsk_vs_part, 'addr', None)
    if tsk_addr is not None:
      self._AddAttribute(volume_system.VolumeAttribute('address', tsk_addr))

    tsk_desc = getattr(self._tsk_vs_part, 'desc', None)
    if tsk_desc is not None:
      self._AddAttribute(volume_system.VolumeAttribute('description', tsk_desc))

    self._extents.append(volume_system.VolumeExtent(
        self._tsk_vs_part.start * self._block_size,
        self._tsk_vs_part.len * self._block_size))


class TSKVolumeSystem(volume_system.VolumeSystem):
  """Class that implements a volume system object using pytsk3."""

  def __init__(self, tsk_image):
    """Initializes the volume system object.

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
          u'Unable to access volume system with error: {0:s}.'.format(
              exception))

    # Note that because pytsk3.Volume_Info does not explicitly defines info
    # we need to check if the attribute exists and has a value other
    # than None. Default to 512 otherwise.
    if (hasattr(self._tsk_volume, 'info') and
        self._tsk_volume.info is not None):
      self.block_size = getattr(self._tsk_volume.info, 'block_size', 512)
    else:
      self.block_size = 512

  def _Parse(self):
    """Extracts sections and volumes from the volume system."""
    volume_index = 0

    # Sticking with the SleuthKit naming convention here, tsk_vs_part is
    # a volume system section (part) and tsk_volume is the volume system.
    for tsk_vs_part in self._tsk_volume:
      # Note that because pytsk3.TSK_VS_PART_INFO does not explicitly defines
      # start and len we need to check if the attribute exists.
      if (not hasattr(tsk_vs_part, 'start') or not hasattr(tsk_vs_part, 'len')):
        continue

      volume_extent = volume_system.VolumeExtent(
          tsk_vs_part.start * self.block_size,
          tsk_vs_part.len * self.block_size)

      self._sections.append(volume_extent)

      # Note that because pytsk3.TSK_VS_PART_INFO does not explicitly defines
      # flags need to check if the attribute exists.
      # The flags are an instance of TSK_VS_PART_FLAG_ENUM.
      if (hasattr(tsk_vs_part, 'flags') and
          tsk_vs_part.flags == pytsk3.TSK_VS_PART_FLAG_ALLOC):
        volume = TSKVolume(tsk_vs_part, volume_index, self.block_size)
        self._AddVolume(volume)
        volume_index += 1
