#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the NTFS path specification implementation."""

import unittest

from dfvfs.path import ntfs_path_spec

from tests.path import test_lib


class NTFSPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the NTFS path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = ntfs_path_spec.NTFSPathSpec(
        data_stream='test', location='\\test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_entry=0, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=3, mft_entry=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\test', mft_entry=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      ntfs_path_spec.NTFSPathSpec(location='\\test', parent=None)

    with self.assertRaises(ValueError):
      ntfs_path_spec.NTFSPathSpec(location=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      ntfs_path_spec.NTFSPathSpec(mft_entry=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      ntfs_path_spec.NTFSPathSpec(
          location='\\test', parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: NTFS, location: \\test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = ntfs_path_spec.NTFSPathSpec(
        data_stream='test', location='\\test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: NTFS, data stream: test, location: \\test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_entry=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: NTFS, MFT entry: 1',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=3, mft_entry=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: NTFS, MFT attribute: 3, MFT entry: 1',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\test', mft_entry=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: NTFS, location: \\test, MFT entry: 1',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
