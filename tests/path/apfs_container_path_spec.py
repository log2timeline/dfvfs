#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the APFS container path specification implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import apfs_container_path_spec

from tests.path import test_lib


class APFSContainerPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the APFS container path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/apfs2', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        volume_index=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/apfs2', volume_index=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      apfs_container_path_spec.APFSContainerPathSpec(parent=None)

    with self.assertRaises(ValueError):
      apfs_container_path_spec.APFSContainerPathSpec(
          parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: APFS_CONTAINER',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/apfs2', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: APFS_CONTAINER, location: /apfs2',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        volume_index=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: APFS_CONTAINER, volume index: 1',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/apfs2', volume_index=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: APFS_CONTAINER, location: /apfs2, volume index: 1',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
