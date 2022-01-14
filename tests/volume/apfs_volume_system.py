#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Apple File System (APFS) volume system."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.volume import apfs_volume_system

from tests import test_lib as shared_test_lib


class APFSVolumeSystemTest(shared_test_lib.BaseTestCase):
  """Tests the Apple File System (APFS) volume system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_path = self._GetTestFilePath(['apfs.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._apfs_container_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, location='/',
        parent=test_raw_path_spec)

  # fsapfsinfo test_data/apfs.raw
  #
  # Apple File System (APFS) information:
  #
  # Container information:
  #     Identifier                       : 697a8dd4-a13a-4437-9397-6202d54ac575
  #     Number of volumes                : 1
  #
  # Volume: 1 information:
  #     Identifier                       : 458ed10d-8ac3-4af1-8dfd-3954d151a3f3
  #     Name                             : apfs_test
  #     Compatible features              : 0x00000002
  #         (NX_FEATURE_LCFD)
  #
  #     Incompatible features            : 0x00000001
  #         (NX_INCOMPAT_VERSION1)
  #
  #     Read-only compatible features    : 0x00000000

  def testIterateVolumes(self):
    """Test the iterate volumes functionality."""
    volume_system = apfs_volume_system.APFSVolumeSystem()

    volume_system.Open(self._apfs_container_path_spec)

    self.assertEqual(volume_system.number_of_sections, 0)
    self.assertEqual(volume_system.number_of_volumes, 1)

    self.assertEqual(volume_system.volume_identifiers, ['apfs1'])

    volume = volume_system.GetVolumeByIndex(0)
    self.assertIsNotNone(volume)

    self.assertEqual(volume.number_of_attributes, 2)
    self.assertEqual(volume.identifier, 'apfs1')

    volume_attribute = volume.GetAttribute('identifier')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(
        volume_attribute.value, '458ed10d-8ac3-4af1-8dfd-3954d151a3f3')

    volume_attribute = volume.GetAttribute('name')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, 'apfs_test')

    volume = volume_system.GetVolumeByIndex(99)
    self.assertIsNone(volume)


if __name__ == '__main__':
  unittest.main()
