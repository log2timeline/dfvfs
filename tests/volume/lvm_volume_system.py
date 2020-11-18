#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Logical Volume Manager (LVM) volume system."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import raw_path_spec
from dfvfs.path import lvm_path_spec
from dfvfs.volume import lvm_volume_system

from tests import test_lib as shared_test_lib


class LVMVolumeSystemTest(shared_test_lib.BaseTestCase):
  """Tests the Logical Volume Manager (LVM) volume system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = self._GetTestFilePath(['lvm.raw'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)
    self._lvm_path_spec = lvm_path_spec.LVMPathSpec(
        location='/', parent=path_spec)

  # vslvminfo lvm.raw
  #
  # Linux Logical Volume Manager (LVM) information:
  # Volume Group (VG):
  #   Name:                         test_volume_group
  #   Identifier:                   OdFqZi-WJfC-35Ok-2Jxv-mcC3-e2OS-QROmeJ
  #   Sequence number:              3
  #   Extent size:                  4.0 MiB (4194304 bytes)
  #   Number of physical volumes:   1
  #   Number of logical volumes:    2
  #
  # Physical Volume (PV): 1
  #   Name:                         pv0
  #   Identifier:                   l051NA-ZitO-CRvE-QizU-JsB2-CqmX-LNDICw
  #   Device path:                  /dev/loop99
  #   Volume size:                  10 MiB (10485760 bytes)
  #
  # Logical Volume (LV): 1
  #   Name:                         test_logical_volume1
  #   Identifier:                   RI0pgm-rdy4-XxcL-5eoK-Easc-fgPq-CWaEJb
  #   Number of segments:           1
  #   Segment: 1
  #     Offset:                     0x00000000 (0)
  #     Size:                       4.0 MiB (4194304 bytes)
  #     Number of stripes:          1
  #     Stripe: 1
  #       Physical volume:          pv0
  #       Data area offset:         0x00000000 (0)
  #
  # Logical Volume (LV): 2
  #   Name:                         test_logical_volume2
  #   Identifier:                   2ySlpP-g1fn-qwMH-h7y9-3u4n-GInp-Pfvvxo
  #   Number of segments:           1
  #   Segment: 1
  #     Offset:                     0x00000000 (0)
  #     Size:                       4.0 MiB (4194304 bytes)
  #     Number of stripes:          1
  #     Stripe: 1
  #       Physical volume:          pv0
  #       Data area offset:         0x00400000 (4194304)

  def testIterateVolumes(self):
    """Test the iterate volumes functionality."""
    volume_system = lvm_volume_system.LVMVolumeSystem()

    volume_system.Open(self._lvm_path_spec)

    self.assertEqual(volume_system.number_of_volumes, 2)

    volume = volume_system.GetVolumeByIndex(0)
    self.assertIsNotNone(volume)

    self.assertEqual(volume.number_of_extents, 1)
    self.assertEqual(volume.number_of_attributes, 1)
    self.assertEqual(volume.identifier, 'lvm1')

    expected_value = 'RI0pgm-rdy4-XxcL-5eoK-Easc-fgPq-CWaEJb'
    volume_attribute = volume.GetAttribute('identifier')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, expected_value)

    volume = volume_system.GetVolumeByIndex(99)
    self.assertIsNone(volume)


if __name__ == '__main__':
  unittest.main()
