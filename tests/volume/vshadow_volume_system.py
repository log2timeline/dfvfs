#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Volume Shadow Snapshots (VSS) volume system."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import vshadow_path_spec
from dfvfs.volume import vshadow_volume_system

from tests import test_lib as shared_test_lib


class VShadowVolumeSystemTest(shared_test_lib.BaseTestCase):
  """Tests the Volume Shadow Snapshot (VSS) volume system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    self._vshadow_path_spec = vshadow_path_spec.VShadowPathSpec(
        location='/', parent=path_spec)

  # qcowmount test_data/vsstest.qcow2 fuse/
  # vshadowinfo fuse/qcow1
  #
  # Volume Shadow Snapshot information:
  #   Number of stores: 2
  #
  # Store: 1
  #   ...
  #   Identifier                : 600f0b69-5bdf-11e3-9d6c-005056c00008
  #   Shadow copy set ID        : 0a4e3901-6abb-48fc-95c2-6ab9e38e9e71
  #   Creation time             : Dec 03, 2013 06:35:09.736378700 UTC
  #   Shadow copy ID            : 4e3c03c2-7bc6-4288-ad96-c1eac1a55f71
  #   Volume size               : 1073741824 bytes
  #   Attribute flags           : 0x00420009
  #
  # Store: 2
  #   Identifier                : 600f0b6d-5bdf-11e3-9d6c-005056c00008
  #   Shadow copy set ID        : 8438a0ee-0f06-443b-ac0c-2905647ca5d6
  #   Creation time             : Dec 03, 2013 06:37:48.919058300 UTC
  #   Shadow copy ID            : 18f1ac6e-959d-436f-bdcc-e797a729e290
  #   Volume size               : 1073741824 bytes
  #   Attribute flags           : 0x00420009

  def testIterateVolumes(self):
    """Test the iterate volumes functionality."""
    volume_system = vshadow_volume_system.VShadowVolumeSystem()

    volume_system.Open(self._vshadow_path_spec)

    self.assertEqual(volume_system.number_of_volumes, 2)

    volume = volume_system.GetVolumeByIndex(1)
    self.assertIsNotNone(volume)

    self.assertEqual(volume.number_of_extents, 1)
    self.assertEqual(volume.number_of_attributes, 4)
    self.assertEqual(volume.identifier, 'vss2')

    expected_value = '600f0b6d-5bdf-11e3-9d6c-005056c00008'
    volume_attribute = volume.GetAttribute('identifier')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, expected_value)

    expected_value = '18f1ac6e-959d-436f-bdcc-e797a729e290'
    volume_attribute = volume.GetAttribute('copy_identifier')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, expected_value)

    expected_value = '8438a0ee-0f06-443b-ac0c-2905647ca5d6'
    volume_attribute = volume.GetAttribute('copy_set_identifier')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, expected_value)

    expected_value = 130305262689190583
    volume_attribute = volume.GetAttribute('creation_time')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, expected_value)

    volume = volume_system.GetVolumeByIndex(7)
    self.assertIsNone(volume)


if __name__ == '__main__':
  unittest.main()
