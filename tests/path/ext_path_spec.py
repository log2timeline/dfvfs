#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the EXT path specification implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import ext_path_spec

from tests.path import test_lib


class EXTPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the EXT path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = ext_path_spec.EXTPathSpec(
        location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = ext_path_spec.EXTPathSpec(
        inode=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = ext_path_spec.EXTPathSpec(
        location='/test', inode=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      ext_path_spec.EXTPathSpec(location='/test', parent=None)

    with self.assertRaises(ValueError):
      ext_path_spec.EXTPathSpec(location=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      ext_path_spec.EXTPathSpec(inode=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      ext_path_spec.EXTPathSpec(
          location='/test', parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = ext_path_spec.EXTPathSpec(
        location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: EXT, location: /test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = ext_path_spec.EXTPathSpec(
        inode=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: EXT, inode: 1',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = ext_path_spec.EXTPathSpec(
        location='/test', inode=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: EXT, inode: 1, location: /test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
