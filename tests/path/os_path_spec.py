#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the operating system path specification implementation."""

import platform
import unittest

from dfvfs.path import os_path_spec

from tests.path import test_lib


class OSPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the operating system path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    if platform.system() == u'Windows':
      test_location = u'C:\\test'
    else:
      test_location = u'/test'

    path_spec = os_path_spec.OSPathSpec(location=test_location)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      _ = os_path_spec.OSPathSpec(
          location=test_location, parent=self._path_spec)

    with self.assertRaises(ValueError):
      _ = os_path_spec.OSPathSpec(location=test_location, bogus=u'BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    if platform.system() == u'Windows':
      test_location = u'C:\\test'
    else:
      test_location = u'/test'

    path_spec = os_path_spec.OSPathSpec(location=test_location)

    self.assertIsNotNone(path_spec)

    expected_comparable = u'\n'.join([
        u'type: OS, location: {0:s}'.format(test_location),
        u''])

    self.assertEqual(path_spec.comparable, expected_comparable)

  def testIsSystemLevel(self):
    """Tests the IsSystemLevel function."""
    if platform.system() == u'Windows':
      test_location = u'C:\\test'
    else:
      test_location = u'/test'

    path_spec = os_path_spec.OSPathSpec(location=test_location)

    self.assertIsNotNone(path_spec)
    self.assertTrue(path_spec.IsSystemLevel())


if __name__ == '__main__':
  unittest.main()
