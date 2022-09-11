#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the HFS path specification implementation."""

import unittest

from dfvfs.path import hfs_path_spec

from tests.path import test_lib


class HFSPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the HFS path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = hfs_path_spec.HFSPathSpec(
        location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = hfs_path_spec.HFSPathSpec(
        data_stream='test', location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = hfs_path_spec.HFSPathSpec(
        identifier=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = hfs_path_spec.HFSPathSpec(
        location='/test', identifier=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      hfs_path_spec.HFSPathSpec(location='/test', parent=None)

    with self.assertRaises(ValueError):
      hfs_path_spec.HFSPathSpec(location=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      hfs_path_spec.HFSPathSpec(identifier=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      hfs_path_spec.HFSPathSpec(
          location='/test', parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = hfs_path_spec.HFSPathSpec(
        location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: HFS, location: /test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = hfs_path_spec.HFSPathSpec(
        data_stream='test', location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: HFS, data stream: test, location: /test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = hfs_path_spec.HFSPathSpec(
        identifier=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: HFS, identifier: 1',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = hfs_path_spec.HFSPathSpec(
        location='/test', identifier=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: HFS, identifier: 1, location: /test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
