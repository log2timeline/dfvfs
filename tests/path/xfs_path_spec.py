#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the XFS path specification implementation."""

import unittest

from dfvfs.path import xfs_path_spec

from tests.path import test_lib


class XFSPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the XFS path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = xfs_path_spec.XFSPathSpec(
        location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = xfs_path_spec.XFSPathSpec(
        inode=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = xfs_path_spec.XFSPathSpec(
        location='/test', inode=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      xfs_path_spec.XFSPathSpec(location='/test', parent=None)

    with self.assertRaises(ValueError):
      xfs_path_spec.XFSPathSpec(location=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      xfs_path_spec.XFSPathSpec(inode=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      xfs_path_spec.XFSPathSpec(
          location='/test', parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = xfs_path_spec.XFSPathSpec(
        location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: XFS, location: /test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = xfs_path_spec.XFSPathSpec(
        inode=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: XFS, inode: 1',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = xfs_path_spec.XFSPathSpec(
        location='/test', inode=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: XFS, inode: 1, location: /test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
