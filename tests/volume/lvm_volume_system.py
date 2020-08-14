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

  # vslvminfo fuse/lvm.raw
  #
  # Linux Logical Volume Manager (LVM) information:
  # Volume Group (VG):
  #   Name:                         test_volume_group
  #   Identifier:                   SN0dH9-7Eic-NCvi-WHj8-76G8-za0g-iJobeq
  #   Sequence number:              2
  #   Extent size:                  4.0 MiB (4194304 bytes)
  #   Number of physical volumes:   1
  #   Number of logical volumes:    1
  #
  # Physical Volume (PV): 1
  #   Name:                         pv0
  #   Identifier:                   K994MB-Sn1r-7rpS-hQEW-DgUP-87Dr-9d0MFa
  #   Device path:                  /dev/loop0
  #   Volume size:                  8.0 MiB (8388608 bytes)
  #
  # Logical Volume (LV): 1
  #   Name:                         test_logical_volume
  #   Identifier:                   0MUZZr-7jgO-iFwW-sSG3-Rb8W-w5td-qAOF8e
  #   Number of segments:           1
  #   Segment: 1
  #     Offset:                     0x00000000 (0)
  #     Size:                       4.0 MiB (4194304 bytes)
  #     Number of stripes:          1
  #     Stripe: 1
  #       Physical volume:          pv0
  #       Data area offset:         0x00000000 (0)

  def testIterateVolumes(self):
    """Test the iterate volumes functionality."""
    volume_system = lvm_volume_system.LVMVolumeSystem()

    volume_system.Open(self._lvm_path_spec)

    self.assertEqual(volume_system.number_of_volumes, 1)

    volume = volume_system.GetVolumeByIndex(0)
    self.assertIsNotNone(volume)

    self.assertEqual(volume.number_of_extents, 1)
    self.assertEqual(volume.number_of_attributes, 1)
    self.assertEqual(volume.identifier, 'lvm1')

    expected_value = '0MUZZr-7jgO-iFwW-sSG3-Rb8W-w5td-qAOF8e'
    volume_attribute = volume.GetAttribute('identifier')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, expected_value)

    volume = volume_system.GetVolumeByIndex(99)
    self.assertIsNone(volume)


if __name__ == '__main__':
  unittest.main()
