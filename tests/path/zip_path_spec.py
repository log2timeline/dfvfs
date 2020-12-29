#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the zip path specification implementation."""

import unittest

from dfvfs.path import zip_path_spec

from tests.path import test_lib


class ZipPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the zip path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      zip_path_spec.ZipPathSpec(location='/test', parent=None)

    with self.assertRaises(ValueError):
      zip_path_spec.ZipPathSpec(location=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      zip_path_spec.ZipPathSpec(
          location='/test', parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: ZIP, location: /test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
