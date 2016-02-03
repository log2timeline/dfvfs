#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the volume system implementation using pyvslvm."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import lvm_path_spec
from dfvfs.volume import lvm_volume_system


class LVMVolumeSystemTest(unittest.TestCase):
  """The unit test for the Logical Volume Manager (LVM) volume system object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = os.path.join(u'test_data', u'lvmtest.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    self._lvm_path_spec = lvm_path_spec.LVMPathSpec(
        location=u'/', parent=path_spec)

  # qcowmount test_data/lvmtest.qcow2 fuse/
  # vslvminfo fuse/qcow1
  #
  # Linux Logical Volume Manager (LVM) information:
  # Volume Group (VG):
  #   Name:                       vg_test
  #   Identifier:                 kZ4S06-lhFY-G4cB-8OQx-SWVg-GrI6-1jEYEf
  #   Sequence number:            3
  #   Extent size:                4194304 bytes
  #   Number of physical volumes: 1
  #   Number of logical volumes:  2
  #
  # Physical Volume (PV): 1
  #   Name:                       pv0
  #   Identifier:                 btEzLa-i0aL-sfS8-Ae9P-QKGU-IhtA-CkpWm7
  #   Device path:                /dev/loop1
  #   Volume size:                16777216 bytes
  #
  # Logical Volume (LV): 1
  #   Name:                       lv_test1
  #   Identifier:                 ldAb7Y-GU1t-qDml-VkAp-qt46-0meR-qJS3vC
  #   Number of segments:         1
  #   Segment: 1
  #     Offset:                   0x00000000 (0)
  #     Size:                     8.0 MiB (8388608 bytes)
  #     Number of stripes:        1
  #     Stripe: 1
  #       Physical volume:        pv0
  #       Data area offset:       0x00000000 (0)
  #
  # Logical Volume (LV): 2
  #   Name:                       lv_test2
  #   Identifier:                 bJxmc8-JEMZ-jXT9-oVeY-40AY-ROro-mCO8Zz
  #   Number of segments:         1
  #   Segment: 1
  #     Offset:                   0x00000000 (0)
  #     Size:                     4.0 MiB (4194304 bytes)
  #     Number of stripes:        1
  #     Stripe: 1
  #       Physical volume:        pv0
  #       Data area offset:       0x00800000 (8388608)

  def testIterateVolumes(self):
    """Test the iterate volumes functionality."""
    volume_system = lvm_volume_system.LVMVolumeSystem()

    volume_system.Open(self._lvm_path_spec)

    self.assertEqual(volume_system.number_of_volumes, 2)

    volume = volume_system.GetVolumeByIndex(1)
    self.assertIsNotNone(volume)

    self.assertEqual(volume.number_of_extents, 1)
    self.assertEqual(volume.number_of_attributes, 1)
    self.assertEqual(volume.identifier, u'lvm2')

    expected_value = u'bJxmc8-JEMZ-jXT9-oVeY-40AY-ROro-mCO8Zz'
    volume_attribute = volume.GetAttribute(u'identifier')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, expected_value)

    volume = volume_system.GetVolumeByIndex(7)
    self.assertIsNone(volume)


if __name__ == '__main__':
  unittest.main()
