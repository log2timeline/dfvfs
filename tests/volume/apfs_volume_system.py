#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Apple File System (APFS) volume system."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import apfs_container_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import raw_path_spec
from dfvfs.path import tsk_partition_path_spec
from dfvfs.volume import apfs_volume_system

from tests import test_lib as shared_test_lib


class APFSVolumeSystemTest(shared_test_lib.BaseTestCase):
  """Tests the Apple File System (APFS) volume system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = self._GetTestFilePath(['apfs.dmg'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)
    self._partition_path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p1', parent=path_spec)
    self._apfs_container_path_spec = (
        apfs_container_path_spec.APFSContainerPathSpec(
            location='/', parent=self._partition_path_spec))

  # fsapfsinfo -o $(( 40 * 512 )) test_data/apfs.dmg
  #
  # Apple File System (APFS) information:
  #
  # Container information:
  #  Identifier	                : 0d411731-1854-49a5-8ef7-1b81cdc57dac
  #  Number of volumes          : 1
  #
  # Volume: 1 information:
  #   Identifier                : 44b5f357-e9b3-483d-893c-3802306b5132
  #   Name                      : SingleVolume

  def testIterateVolumes(self):
    """Test the iterate volumes functionality."""
    volume_system = apfs_volume_system.APFSVolumeSystem()

    volume_system.Open(self._apfs_container_path_spec)

    self.assertEqual(volume_system.number_of_volumes, 1)

    volume = volume_system.GetVolumeByIndex(0)
    self.assertIsNotNone(volume)

    self.assertEqual(volume.number_of_attributes, 2)
    self.assertEqual(volume.identifier, 'apfs1')

    expected_value = '44b5f357-e9b3-483d-893c-3802306b5132'
    volume_attribute = volume.GetAttribute('identifier')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, expected_value)

    volume_attribute = volume.GetAttribute('name')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, 'SingleVolume')

    volume = volume_system.GetVolumeByIndex(99)
    self.assertIsNone(volume)


if __name__ == '__main__':
  unittest.main()
