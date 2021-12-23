#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the GUID Partition Table (GPT) volume system."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.volume import gpt_volume_system

from tests import test_lib as shared_test_lib


class GPTVolumeSystemTest(shared_test_lib.BaseTestCase):
  """Tests the GUID Partition Table (GPT) volume system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_path = self._GetTestFilePath(['gpt.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._gpt_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GPT, location='/',
        parent=test_raw_path_spec)

  # vsgptinfo gpt.raw
  #
  # GUID Partition Table (GPT) information:
  #     Disk identifier         : e86e657a-d840-4c09-afe3-a1a5f665cf44
  #     Bytes per sector        : 512
  #     Number of partitions    : 2
  #
  # Partition: 1
  #     Identifier              : 1e25588c-27a9-4094-868c-2f257021f87b
  #     Type identifier         : 0fc63daf-8483-4772-8e79-3d69d8477de4
  #     Type                    : 0x00 (Empty)
  #     Offset                  : 1048576 (0x00100000)
  #     Size                    : 65536
  #
  # Partition: 2
  #     Identifier              : 53d86ccf-3188-4b54-90d8-81866426b70a
  #     Type identifier         : 0fc63daf-8483-4772-8e79-3d69d8477de4
  #     Type                    : 0x00 (Empty)
  #     Offset                  : 2097152 (0x00200000)
  #     Size                    : 65536

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

    volume_attribute = volume.GetAttribute('identifier')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(
        volume_attribute.value, '1e25588c-27a9-4094-868c-2f257021f87b')

    volume_extent = volume.extents[0]
    self.assertIsNotNone(volume_extent)
    self.assertEqual(volume_extent.offset, 1048576)
    self.assertEqual(volume_extent.size, 65536)
    self.assertEqual(volume_extent.extent_type, volume_extent.EXTENT_TYPE_DATA)

    volume = volume_system.GetVolumeByIndex(99)
    self.assertIsNone(volume)


if __name__ == '__main__':
  unittest.main()
