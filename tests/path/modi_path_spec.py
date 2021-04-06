#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Mac OS disk image path specification implementation."""

import unittest

from dfvfs.path import modi_path_spec

from tests.path import test_lib


class MODIPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the Mac OS disk image path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = modi_path_spec.MODIPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      modi_path_spec.MODIPathSpec(parent=None)

    with self.assertRaises(ValueError):
      modi_path_spec.MODIPathSpec(parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = modi_path_spec.MODIPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: MODI',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
