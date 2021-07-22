#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Logical Volume Manager (LVM) volume system."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.volume import lvm_volume_system

from tests import test_lib as shared_test_lib


class LVMVolumeSystemTest(shared_test_lib.BaseTestCase):
  """Tests the Logical Volume Manager (LVM) volume system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_path = self._GetTestFilePath(['lvm.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._lvm_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_LVM, location='/',
        parent=test_raw_path_spec)

  # vslvminfo lvm.raw
  # vslvminfo 20210524
  #
  # Linux Logical Volume Manager (LVM) information:
  # Volume Group (VG):
  #     Name:                          test_volume_group
  #     Identifier:                    Lu8jtE-dBED-jxdl-bAXG-vmAA-Oh9y-KCiNMy
  #     Sequence number:               3
  #     Extent size:                   4.0 MiB (4194304 bytes)
  #     Number of physical volumes:    1
  #     Number of logical volumes:     2
  #
  # Physical Volume (PV): 1
  #     Name:                          pv0
  #     Identifier:                    V9N6H5-MXlo-JmEE-TLHs-KyAo-kLv5-JL0RY7
  #     Device path:                   /dev/loop99
  #     Volume size:                   10 MiB (10485760 bytes)
  #
  # Logical Volume (LV): 1
  #     Name:                          test_logical_volume1
  #     Identifier:                    EMfcGR-KAOf-VrvI-yqth-fmz0-Ylmx-xepAJq
  #     Number of segments:            1
  #     Segment: 1
  #         Offset:                    0x00000000 (0)
  #         Size:                      4.0 MiB (4194304 bytes)
  #         Number of stripes:         1
  #         Stripe: 1
  #             Physical volume:       pv0
  #             Data area offset:      0x00000000 (0)
  #
  # Logical Volume (LV): 2
  #     Name:                          test_logical_volume2
  #     Identifier:                    UbmaM4-4OCn-m0mb-uw5D-kCjp-2hi1-M6kWCX
  #     Number of segments:            1
  #     Segment: 1
  #         Offset:                    0x00000000 (0)
  #         Size:                      4.0 MiB (4194304 bytes)
  #         Number of stripes:         1
  #         Stripe: 1
  #             Physical volume:       pv0
  #             Data area offset:      0x00400000 (4194304)

  def testIterateVolumes(self):
    """Test the iterate volumes functionality."""
    volume_system = lvm_volume_system.LVMVolumeSystem()

    volume_system.Open(self._lvm_path_spec)

    self.assertEqual(volume_system.number_of_sections, 0)
    self.assertEqual(volume_system.number_of_volumes, 2)

    self.assertEqual(volume_system.volume_identifiers, ['lvm1', 'lvm2'])

    volume = volume_system.GetVolumeByIndex(0)
    self.assertIsNotNone(volume)

    self.assertEqual(volume.number_of_extents, 1)
    self.assertEqual(volume.number_of_attributes, 1)
    self.assertEqual(volume.identifier, 'lvm1')

    expected_value = 'EMfcGR-KAOf-VrvI-yqth-fmz0-Ylmx-xepAJq'
    volume_attribute = volume.GetAttribute('identifier')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, expected_value)

    volume = volume_system.GetVolumeByIndex(99)
    self.assertIsNone(volume)


if __name__ == '__main__':
  unittest.main()
