#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the helper functions for APFS container support."""

from __future__ import unicode_literals

import unittest

from dfvfs.lib import apfs_container
from dfvfs.path import apfs_container_path_spec

from tests.path import test_lib


class APFSContainerHelperTest(test_lib.PathSpecTestCase):
  """Tests for the helper functions for APFS container support."""

  def testAPFSContainerPathSpecGetVolumeIndex(self):
    """Tests the APFSContainerPathSpecGetVolumeIndex function."""
    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    volume_index = apfs_container.APFSContainerPathSpecGetVolumeIndex(path_spec)
    self.assertIsNone(volume_index)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/apfs2', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    volume_index = apfs_container.APFSContainerPathSpecGetVolumeIndex(path_spec)
    self.assertEqual(volume_index, 1)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        volume_index=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    volume_index = apfs_container.APFSContainerPathSpecGetVolumeIndex(path_spec)
    self.assertEqual(volume_index, 1)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/apfs2', volume_index=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    volume_index = apfs_container.APFSContainerPathSpecGetVolumeIndex(path_spec)
    self.assertEqual(volume_index, 1)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/apfs', parent=self._path_spec)

    volume_index = apfs_container.APFSContainerPathSpecGetVolumeIndex(path_spec)
    self.assertIsNone(volume_index)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/apfs101', parent=self._path_spec)

    volume_index = apfs_container.APFSContainerPathSpecGetVolumeIndex(path_spec)
    self.assertIsNone(volume_index)


if __name__ == '__main__':
  unittest.main()
