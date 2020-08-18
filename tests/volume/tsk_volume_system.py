#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the SleuthKit (TSK) volume system."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import tsk_partition_path_spec
from dfvfs.volume import tsk_volume_system

from tests import test_lib as shared_test_lib


class TSKVolumeSystemTest(shared_test_lib.BaseTestCase):
  """Tests the SleuthKit (TSK) volume system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = self._GetTestFilePath(['mbr.raw'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._tsk_path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/', parent=path_spec)

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

    volume = volume_system.GetVolumeByIndex(1)
    self.assertIsNotNone(volume)

    self.assertEqual(volume.number_of_extents, 1)
    self.assertEqual(volume.number_of_attributes, 2)
    self.assertEqual(volume.identifier, 'p2')

    expected_value = 6
    volume_attribute = volume.GetAttribute('address')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, expected_value)

    expected_value = 'Linux (0x83)'
    volume_attribute = volume.GetAttribute('description')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, expected_value)

    volume = volume_system.GetVolumeByIndex(7)
    self.assertIsNone(volume)


if __name__ == '__main__':
  unittest.main()
