#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the NTFS path specification implementation."""

import unittest

from tests.path import test_lib
from dfvfs.path import ntfs_path_spec


class NTFSPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the NTFS path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=u'\\test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = ntfs_path_spec.NTFSPathSpec(
        data_stream=u'test', location=u'\\test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_entry=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=3, mft_entry=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=u'\\test', mft_entry=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      _ = ntfs_path_spec.NTFSPathSpec(location=u'\\test', parent=None)

    with self.assertRaises(ValueError):
      _ = ntfs_path_spec.NTFSPathSpec(location=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      _ = ntfs_path_spec.NTFSPathSpec(mft_entry=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      _ = ntfs_path_spec.NTFSPathSpec(
          location=u'\\test', parent=self._path_spec, bogus=u'BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=u'\\test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = u'\n'.join([
        u'type: TEST',
        u'type: NTFS, location: \\test',
        u''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = ntfs_path_spec.NTFSPathSpec(
        data_stream=u'test', location=u'\\test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = u'\n'.join([
        u'type: TEST',
        u'type: NTFS, data stream: test, location: \\test',
        u''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_entry=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = u'\n'.join([
        u'type: TEST',
        u'type: NTFS, MFT entry: 1',
        u''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=3, mft_entry=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = u'\n'.join([
        u'type: TEST',
        u'type: NTFS, MFT attribute: 3, MFT entry: 1',
        u''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=u'\\test', mft_entry=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = u'\n'.join([
        u'type: TEST',
        u'type: NTFS, location: \\test, MFT entry: 1',
        u''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
