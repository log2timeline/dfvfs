#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the operating system path specification implementation."""

import platform
import unittest

from dfvfs.path import mount_path_spec
from dfvfs.path import os_path_spec

from tests.path import test_lib


class OSPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the operating system path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    if platform.system() == 'Windows':
      test_location = 'C:\\test'
    else:
      test_location = '/test'

    path_spec = os_path_spec.OSPathSpec(location=test_location)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      os_path_spec.OSPathSpec(
          location=test_location, parent=self._path_spec)

    with self.assertRaises(ValueError):
      os_path_spec.OSPathSpec(location=test_location, bogus='BOGUS')

    test_mount_path_spec = mount_path_spec.MountPathSpec(identifier='C')
    path_spec = os_path_spec.OSPathSpec(
        location=test_location, parent=test_mount_path_spec)

    self.assertIsNotNone(path_spec)

  def testComparable(self):
    """Tests the path specification comparable property."""
    if platform.system() == 'Windows':
      test_location = 'C:\\test'
    else:
      test_location = '/test'

    path_spec = os_path_spec.OSPathSpec(location=test_location)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        f'type: OS, location: {test_location:s}',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

  def testIsSystemLevel(self):
    """Tests the IsSystemLevel function."""
    if platform.system() == 'Windows':
      test_location = 'C:\\test'
    else:
      test_location = '/test'

    path_spec = os_path_spec.OSPathSpec(location=test_location)

    self.assertIsNotNone(path_spec)
    self.assertTrue(path_spec.IsSystemLevel())


if __name__ == '__main__':
  unittest.main()
