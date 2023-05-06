#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Apple Partition Map (APM) volume system."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.volume import apm_volume_system

from tests import test_lib as shared_test_lib


class APMVolumeSystemTest(shared_test_lib.BaseTestCase):
  """Tests the Apple Partition Map (APM) volume system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_path = self._GetTestFilePath(['apm.dmg'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_modi_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_MODI, parent=test_os_path_spec)
    self._apm_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APM, location='/',
        parent=test_modi_path_spec)

  # vsapminfo apm.dmg
  #
  # Apple Partition Map (APM) information:
  # 	Bytes per sector        : 512
  # 	Number of partitions    : 2
  #
  # Partition: 1
  # 	Type                    : Apple_HFS
  # 	Name                    : disk image
  # 	Offset                  : 32768 (0x00008000)
  # 	Size                    : 4153344
  # 	Status flags            : 0x40000033
  # 		Is valid
  # 		Is allocated
  # 		Is readable
  # 		Is writeable
  # 		Automatic mount at startup
  #
  # Partition: 2
  # 	Type                    : Apple_Free
  # 	Offset                  : 4186112 (0x003fe000)
  # 	Size                    : 8192
  # 	Status flags            : 0x00000000

  def testIterateVolumes(self):
    """Test the iterate volumes functionality."""
    volume_system = apm_volume_system.APMVolumeSystem()

    volume_system.Open(self._apm_path_spec)

    self.assertEqual(volume_system.number_of_sections, 0)
    self.assertEqual(volume_system.number_of_volumes, 2)

    self.assertEqual(volume_system.volume_identifiers, ['p1', 'p2'])

    volume = volume_system.GetVolumeByIndex(0)
    self.assertIsNotNone(volume)

    self.assertEqual(volume.number_of_extents, 1)
    self.assertEqual(volume.number_of_attributes, 1)
    self.assertEqual(volume.identifier, 'p1')

    volume_attribute = volume.GetAttribute('name')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, 'disk image')

    volume_extent = volume.extents[0]
    self.assertIsNotNone(volume_extent)
    self.assertEqual(volume_extent.offset, 32768)
    self.assertEqual(volume_extent.size, 4153344)
    self.assertEqual(volume_extent.extent_type, volume_extent.EXTENT_TYPE_DATA)

    volume = volume_system.GetVolumeByIndex(99)
    self.assertIsNone(volume)


if __name__ == '__main__':
  unittest.main()
