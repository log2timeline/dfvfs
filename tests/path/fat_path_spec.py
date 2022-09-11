#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the FAT path specification implementation."""

import unittest

from dfvfs.path import fat_path_spec

from tests.path import test_lib


class FATPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the FAT path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = fat_path_spec.FATPathSpec(
        location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = fat_path_spec.FATPathSpec(
        identifier=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = fat_path_spec.FATPathSpec(
        location='/test', identifier=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      fat_path_spec.FATPathSpec(location='/test', parent=None)

    with self.assertRaises(ValueError):
      fat_path_spec.FATPathSpec(location=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      fat_path_spec.FATPathSpec(identifier=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      fat_path_spec.FATPathSpec(
          location='/test', parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = fat_path_spec.FATPathSpec(
        location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: FAT, location: /test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = fat_path_spec.FATPathSpec(
        identifier=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: FAT, identifier: 1',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = fat_path_spec.FATPathSpec(
        location='/test', identifier=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: FAT, identifier: 1, location: /test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
