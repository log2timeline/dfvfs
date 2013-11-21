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
"""The Virtual File System (VFS) volume system interface."""

import abc


class VolumeExtent(object):
  """The VFS volume extent object."""

  EXTENT_TYPE_DATA = 0
  EXTENT_TYPE_SPARSE = 1

  def __init__(self, offset, size, extent_type=EXTENT_TYPE_DATA):
    """Initializes the volume extent object.

    Args:
      offset: the start offset of the extent, in bytes.
      size: the size of the extent, in bytes.
      extent_type: optional type of extent, the default is
                   EXTENT_TYPE_DATA.
    """
    super(VolumeExtent, self).__init__()
    self.offset = offset
    self.size = size
    self.extent_type = extent_type


class Volume(object):
  """The VFS volume interface."""

  def __init__(self):
    """Initializes the volume extent object."""
    super(Volume, self).__init__()
    self.extents = []

  def AddExtent(self, volume_extent):
    """Adds an extent to the volume.

    Args:
      volume_extent: the volume extent object (VolumeExtent).
    """
    self.extents.append(volume_extent)


class VolumeSystem(object):
  """The VFS volume system interface."""

  def __init__(self):
    """Initializes the volume system object."""
    super(VolumeSystem, self).__init__()
    self._sections = []
    self._volumes = []
    self._is_parsed = False

  @abc.abstractmethod
  def _Parse(self):
    """Extracts sections and volumes from the volume system."""

  @property
  def number_of_sections(self):
    """The number of sections."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return len(self._sections)

  @property
  def sections(self):
    """The sections."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    for section in self._sections:
      yield section

  def GetSectionIndex(self, section_index):
    """Retrieves a specific section based on the index.

    Args:
      section_index: the index of the section.
    """
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return self._sections[section_index]

  @property
  def number_of_volumes(self):
    """The number of volumes."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return len(self._volumes)

  @property
  def volumes(self):
    """The volumes."""
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    for volume in self._volumes:
      yield volume

  def GetVolumeByIndex(self, volume_index):
    """Retrieves a specific volume based on the index.

    Args:
      volume_index: the index of the volume.
    """
    if not self._is_parsed:
      self._Parse()
      self._is_parsed = True

    return self._volumes[volume_index]
