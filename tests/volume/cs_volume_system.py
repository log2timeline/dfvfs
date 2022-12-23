#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Core Storage (CS) volume system."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.volume import cs_volume_system

from tests import test_lib as shared_test_lib


class CSVolumeSystemTest(shared_test_lib.BaseTestCase):
  """Tests the Core Storage (CS) volume system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_path = self._GetTestFilePath(['fvdetest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_qcow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_QCOW, parent=test_os_path_spec)
    test_gpt_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GPT, location='/p1',
        parent=test_qcow_path_spec)
    self._cs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, location='/',
        parent=test_gpt_path_spec)

  def testIterateVolumes(self):
    """Test the iterate volumes functionality."""
    volume_system = cs_volume_system.CSVolumeSystem()

    volume_system.Open(self._cs_path_spec)

    self.assertEqual(volume_system.number_of_sections, 0)
    self.assertEqual(volume_system.number_of_volumes, 1)

    self.assertEqual(volume_system.volume_identifiers, ['cs1'])

    volume = volume_system.GetVolumeByIndex(0)
    self.assertIsNotNone(volume)

    self.assertEqual(volume.number_of_extents, 1)
    self.assertEqual(volume.number_of_attributes, 1)
    self.assertEqual(volume.identifier, 'cs1')

    expected_value = '420af122-cf73-4a30-8b0a-a593a65fbef5'
    volume_attribute = volume.GetAttribute('identifier')
    self.assertIsNotNone(volume_attribute)
    self.assertEqual(volume_attribute.value, expected_value)

    volume = volume_system.GetVolumeByIndex(99)
    self.assertIsNone(volume)


if __name__ == '__main__':
  unittest.main()
