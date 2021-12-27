#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the volume system factory."""

import unittest

from dfvfs.lib import definitions
from dfvfs.volume import factory
from dfvfs.volume import volume_system


class TestVolumeSystem(volume_system.VolumeSystem):
  """Test volume system."""

  TYPE_INDICATOR = 'TEST'

  def _Parse(self):
    """Extracts sections and volumes from the volume system."""
    return


class FactoryTest(unittest.TestCase):
  """Class to test the volume system factory object."""

  def testVolumeSystemRegistration(self):
    """Tests the RegisterVolumeSystem and DeregisterVolumeSystem functions."""
    # pylint: disable=protected-access
    number_of_volume_system_types = len(factory.Factory._volume_system_types)

    factory.Factory.RegisterVolumeSystem(TestVolumeSystem)
    self.assertEqual(
        len(factory.Factory._volume_system_types),
        number_of_volume_system_types + 1)

    with self.assertRaises(KeyError):
      factory.Factory.RegisterVolumeSystem(TestVolumeSystem)

    factory.Factory.DeregisterVolumeSystem(TestVolumeSystem)
    self.assertEqual(
        len(factory.Factory._volume_system_types),
        number_of_volume_system_types)

  def testNewVolumeSystem(self):
    """Tests the NewVolumeSystem function."""
    test_volume_system = factory.Factory.NewVolumeSystem(
        definitions.TYPE_INDICATOR_GPT)

    self.assertIsNotNone(test_volume_system)


if __name__ == '__main__':
  unittest.main()
