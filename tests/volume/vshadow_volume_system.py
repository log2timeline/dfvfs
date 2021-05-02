#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Volume Shadow Snapshots (VSS) volume system."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.volume import vshadow_volume_system

from tests import test_lib as shared_test_lib


class VShadowVolumeSystemTest(shared_test_lib.BaseTestCase):
  """Tests the Volume Shadow Snapshot (VSS) volume system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_path = self._GetTestFilePath(['vss.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._vshadow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, location='/',
        parent=test_raw_path_spec)

  # vshadowinfo test_data/vss.raw
  # vshadowinfo 20210425
  #
  # Volume Shadow Snapshot information:
  #     Number of stores:	2
  #
  # Store: 1
  #     Identifier          : de81cc22-aa8b-11eb-9339-8cdcd4557abc
  #     Shadow copy set ID  : 6c5c9cd2-ea46-4c70-a4a8-568fdabd27c1
  #     Creation time       : May 01, 2021 17:40:03.223030400 UTC
  #     Shadow copy ID      : 2c6c6cc8-2b97-41da-a030-4add838ae8f6
  #     Volume size         : 78 MiB (82771968 bytes)
  #     Attribute flags     : 0x00420009
  #
  # Store: 2
  #     Identifier          : de81cc2b-aa8b-11eb-9339-8cdcd4557abc
  #     Shadow copy set ID  : b4f4b9d6-1cf2-4bfc-b1a3-c2f6e9628ef9
  #     Creation time       : May 01, 2021 17:41:28.224986300 UTC
  #     Shadow copy ID      : 19e1881a-c184-4ec4-908e-766ba3373e8a
  #     Volume size         : 78 MiB (82771968 bytes)
  #     Attribute flags     : 0x00420009

  def testIterateVolumes(self):
    """Test the iterate volumes functionality."""
    volume_system = vshadow_volume_system.VShadowVolumeSystem()

    volume_system.Open(self._vshadow_path_spec)

    self.assertEqual(volume_system.number_of_sections, 0)
    self.assertEqual(volume_system.number_of_volumes, 2)

    self.assertEqual(volume_system.volume_identifiers, ['vss1', 'vss2'])

    volume = volume_system.GetVolumeByIndex(1)
    self.assertIsNotNone(volume)

    self.assertEqual(volume.number_of_extents, 1)
    self.assertEqual(volume.number_of_attributes, 4)
    self.assertEqual(volume.identifier, 'vss2')

    expected_value = 'de81cc2b-aa8b-11eb-9339-8cdcd4557abc'
    volume_attribute = volume.GetAttribute('identifier')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, expected_value)

    expected_value = '19e1881a-c184-4ec4-908e-766ba3373e8a'
    volume_attribute = volume.GetAttribute('copy_identifier')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, expected_value)

    expected_value = 'b4f4b9d6-1cf2-4bfc-b1a3-c2f6e9628ef9'
    volume_attribute = volume.GetAttribute('copy_set_identifier')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, expected_value)

    expected_value = 132643644882249863
    volume_attribute = volume.GetAttribute('creation_time')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, expected_value)

    volume = volume_system.GetVolumeByIndex(7)
    self.assertIsNone(volume)


if __name__ == '__main__':
  unittest.main()
