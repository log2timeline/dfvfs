#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the SleuthKit (TSK) volume system."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.volume import tsk_volume_system

from tests import test_lib as shared_test_lib


class TSKVolumeSystemTestAPM(shared_test_lib.BaseTestCase):
  """Tests the SleuthKit (TSK) volume system on APM."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_path = self._GetTestFilePath(['apm.dmg'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._tsk_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/',
        parent=test_os_path_spec)

  # mmls test_data/apm.dmg
  # MAC Partition Map
  # Offset Sector: 0
  # Units are in 512-byte sectors
  #
  #       Slot      Start        End          Length       Description
  # 000:  -------   0000000000   0000000000   0000000001   Unallocated
  # 001:  000       0000000001   0000000063   0000000063   Apple_partition_map
  # 002:  Meta      0000000001   0000000003   0000000003   Table
  # 003:  001       0000000064   0000008175   0000008112   Apple_HFS
  # 004:  002       0000008176   0000008191   0000000016   Apple_Free

  def testIterateVolumes(self):
    """Test the iterate volumes functionality."""
    volume_system = tsk_volume_system.TSKVolumeSystem()
    volume_system.Open(self._tsk_path_spec)

    self.assertEqual(volume_system.bytes_per_sector, 512)

    self.assertEqual(volume_system.number_of_sections, 5)
    self.assertEqual(volume_system.number_of_volumes, 1)

    self.assertEqual(volume_system.volume_identifiers, ['p1'])

    volume = volume_system.GetVolumeByIndex(0)
    self.assertIsNotNone(volume)

    self.assertEqual(volume.number_of_extents, 1)
    self.assertEqual(volume.number_of_attributes, 2)
    self.assertEqual(volume.identifier, 'p1')

    volume_attribute = volume.GetAttribute('address')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, 3)

    volume_attribute = volume.GetAttribute('description')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, 'Apple_HFS')

    volume_extent = volume.extents[0]
    self.assertIsNotNone(volume_extent)
    self.assertEqual(volume_extent.offset, 64 * 512)
    self.assertEqual(volume_extent.size, 8112 * 512)
    self.assertEqual(volume_extent.extent_type, volume_extent.EXTENT_TYPE_DATA)

    volume = volume_system.GetVolumeByIndex(9)
    self.assertIsNone(volume)


class TSKVolumeSystemTestGPT(shared_test_lib.BaseTestCase):
  """Tests the SleuthKit (TSK) volume system on GPT."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_path = self._GetTestFilePath(['gpt.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._tsk_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/',
        parent=test_os_path_spec)

  # mmls test_data/gpt.raw
  # GUID Partition Table (EFI)
  # Offset Sector: 0
  # Units are in 512-byte sectors
  #
  #       Slot      Start        End          Length       Description
  # 000:  Meta      0000000000   0000000000   0000000001   Safety Table
  # 001:  -------   0000000000   0000002047   0000002048   Unallocated
  # 002:  Meta      0000000001   0000000001   0000000001   GPT Header
  # 003:  Meta      0000000002   0000000033   0000000032   Partition Table
  # 004:  000       0000002048   0000002175   0000000128   Linux filesystem
  # 005:  -------   0000002176   0000004095   0000001920   Unallocated
  # 006:  001       0000004096   0000004223   0000000128   Linux filesystem
  # 007:  -------   0000004224   0000008191   0000003968   Unallocated

  def testIterateVolumes(self):
    """Test the iterate volumes functionality."""
    volume_system = tsk_volume_system.TSKVolumeSystem()
    volume_system.Open(self._tsk_path_spec)

    self.assertEqual(volume_system.bytes_per_sector, 512)

    self.assertEqual(volume_system.number_of_sections, 8)
    self.assertEqual(volume_system.number_of_volumes, 2)

    self.assertEqual(volume_system.volume_identifiers, ['p1', 'p2'])

    volume = volume_system.GetVolumeByIndex(1)
    self.assertIsNotNone(volume)

    self.assertEqual(volume.number_of_extents, 1)
    self.assertEqual(volume.number_of_attributes, 2)
    self.assertEqual(volume.identifier, 'p2')

    volume_attribute = volume.GetAttribute('address')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, 6)

    volume_attribute = volume.GetAttribute('description')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, 'Linux filesystem')

    volume_extent = volume.extents[0]
    self.assertIsNotNone(volume_extent)
    self.assertEqual(volume_extent.offset, 4096 * 512)
    self.assertEqual(volume_extent.size, 128 * 512)
    self.assertEqual(volume_extent.extent_type, volume_extent.EXTENT_TYPE_DATA)

    volume = volume_system.GetVolumeByIndex(9)
    self.assertIsNone(volume)


class TSKVolumeSystemTestMBR(shared_test_lib.BaseTestCase):
  """Tests the SleuthKit (TSK) volume system on MBR."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_path = self._GetTestFilePath(['mbr.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._tsk_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/',
        parent=test_os_path_spec)

  # mmls test_data/mbr.raw
  # DOS Partition Table
  # Offset Sector: 0
  # Units are in 512-byte sectors
  #
  #       Slot      Start        End          Length       Description
  # 000:  Meta      0000000000   0000000000   0000000001   Primary Table (#0)
  # 001:  -------   0000000000   0000000000   0000000001   Unallocated
  # 002:  000:000   0000000001   0000000129   0000000129   Linux (0x83)
  # 003:  Meta      0000000130   0000008191   0000008062   DOS Extended (0x05)
  # 004:  Meta      0000000130   0000000130   0000000001   Extended Table (#1)
  # 005:  -------   0000000130   0000000130   0000000001   Unallocated
  # 006:  001:000   0000000131   0000000259   0000000129   Linux (0x83)
  # 007:  -------   0000000260   0000008191   0000007932   Unallocated

  def testIterateVolumes(self):
    """Test the iterate volumes functionality."""
    volume_system = tsk_volume_system.TSKVolumeSystem()
    volume_system.Open(self._tsk_path_spec)

    self.assertEqual(volume_system.bytes_per_sector, 512)

    self.assertEqual(volume_system.number_of_sections, 8)
    self.assertEqual(volume_system.number_of_volumes, 2)

    self.assertEqual(volume_system.volume_identifiers, ['p1', 'p2'])

    volume = volume_system.GetVolumeByIndex(1)
    self.assertIsNotNone(volume)

    self.assertEqual(volume.number_of_extents, 1)
    self.assertEqual(volume.number_of_attributes, 2)
    self.assertEqual(volume.identifier, 'p2')

    volume_attribute = volume.GetAttribute('address')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, 6)

    volume_attribute = volume.GetAttribute('description')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, 'Linux (0x83)')

    volume_extent = volume.extents[0]
    self.assertIsNotNone(volume_extent)
    self.assertEqual(volume_extent.offset, 131 * 512)
    self.assertEqual(volume_extent.size, 129 * 512)
    self.assertEqual(volume_extent.extent_type, volume_extent.EXTENT_TYPE_DATA)

    volume = volume_system.GetVolumeByIndex(9)
    self.assertIsNone(volume)


if __name__ == '__main__':
  unittest.main()
