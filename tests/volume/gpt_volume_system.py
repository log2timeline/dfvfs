#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the GUID Partition Table (GPT) volume system."""

import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import raw_path_spec
from dfvfs.path import gpt_path_spec
from dfvfs.volume import gpt_volume_system

from tests import test_lib as shared_test_lib


class GPTVolumeSystemTest(shared_test_lib.BaseTestCase):
  """Tests the GUID Partition Table (GPT) volume system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = self._GetTestFilePath(['gpt.raw'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)
    self._gpt_path_spec = gpt_path_spec.GPTPathSpec(
        location='/', parent=path_spec)

  # vsgptinfo gpt.raw
  #
  # GUID Partition Table (GPT) information:
  #   Disk identifier      : 25271092-82a1-4e85-9be8-2eb59926af3f
  #   Bytes per sector     : 512
  #   Number of partitions : 2
  #
  # Partition: 1
  #   Identifier           : b6d37ab4-051f-4556-97d2-ad1f8a609644
  #   Type identifier      : 0fc63daf-8483-4772-8e79-3d69d8477de4
  #   Type                 : 0x00 (Empty)
  #   Offset               : 1048576 (0x00100000)
  #   Size                 : 65024
  #
  # Partition: 2
  #   Identifier           : a03faa35-d9a1-4315-a644-681506850073
  #   Type identifier      : 0fc63daf-8483-4772-8e79-3d69d8477de4
  #   Type                 : 0x00 (Empty)
  #   Offset               : 2097152 (0x00200000)
  #   Size                 : 65024

  def testIterateVolumes(self):
    """Test the iterate volumes functionality."""
    volume_system = gpt_volume_system.GPTVolumeSystem()

    volume_system.Open(self._gpt_path_spec)

    self.assertEqual(volume_system.number_of_sections, 0)
    self.assertEqual(volume_system.number_of_volumes, 2)

    self.assertEqual(volume_system.volume_identifiers, ['p1', 'p2'])

    volume = volume_system.GetVolumeByIndex(0)
    self.assertIsNotNone(volume)

    self.assertEqual(volume.number_of_extents, 1)
    self.assertEqual(volume.number_of_attributes, 1)
    self.assertEqual(volume.identifier, 'p1')

    expected_value = 'b6d37ab4-051f-4556-97d2-ad1f8a609644'
    volume_attribute = volume.GetAttribute('identifier')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, expected_value)

    volume = volume_system.GetVolumeByIndex(99)
    self.assertIsNone(volume)


if __name__ == '__main__':
  unittest.main()
