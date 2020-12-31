#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the helper functions for Apple File System (APFS) support."""

import unittest

from dfvfs.lib import apfs_helper
from dfvfs.lib import definitions
from dfvfs.path import apfs_container_path_spec
from dfvfs.path import factory as path_spec_factory
from dfvfs.path import fake_path_spec
from dfvfs.resolver import context
from dfvfs.resolver import resolver

from tests import test_lib as shared_test_lib


class APFSContainerHelperTest(shared_test_lib.BaseTestCase):
  """Tests for the helper functions for Apple File System (APFS) support."""

  _APFS_PASSWORD = 'apfs-TEST'

  def testAPFSContainerPathSpecGetVolumeIndex(self):
    """Tests the APFSContainerPathSpecGetVolumeIndex function."""
    test_fake_path_spec = fake_path_spec.FakePathSpec(location='/')

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        parent=test_fake_path_spec)

    self.assertIsNotNone(path_spec)

    volume_index = apfs_helper.APFSContainerPathSpecGetVolumeIndex(path_spec)
    self.assertIsNone(volume_index)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/apfs2', parent=test_fake_path_spec)

    self.assertIsNotNone(path_spec)

    volume_index = apfs_helper.APFSContainerPathSpecGetVolumeIndex(path_spec)
    self.assertEqual(volume_index, 1)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        volume_index=1, parent=test_fake_path_spec)

    self.assertIsNotNone(path_spec)

    volume_index = apfs_helper.APFSContainerPathSpecGetVolumeIndex(path_spec)
    self.assertEqual(volume_index, 1)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/apfs2', volume_index=1, parent=test_fake_path_spec)

    self.assertIsNotNone(path_spec)

    volume_index = apfs_helper.APFSContainerPathSpecGetVolumeIndex(path_spec)
    self.assertEqual(volume_index, 1)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/apfs', parent=test_fake_path_spec)

    volume_index = apfs_helper.APFSContainerPathSpecGetVolumeIndex(path_spec)
    self.assertIsNone(volume_index)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/apfs101', parent=test_fake_path_spec)

    volume_index = apfs_helper.APFSContainerPathSpecGetVolumeIndex(path_spec)
    self.assertIsNone(volume_index)

  def testAPFSUnlockVolumeOnAPFS(self):
    """Tests the APFSUnlockVolume function on an APFS image."""
    resolver_context = context.Context()

    test_path = self._GetTestFilePath(['apfs.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    test_apfs_container_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, location='/apfs1',
        parent=test_raw_path_spec)

    container_file_entry = resolver.Resolver.OpenFileEntry(
        test_apfs_container_path_spec, resolver_context=resolver_context)
    fsapfs_volume = container_file_entry.GetAPFSVolume()

    is_unlocked = apfs_helper.APFSUnlockVolume(
        fsapfs_volume, test_apfs_container_path_spec,
        resolver.Resolver.key_chain)
    self.assertTrue(is_unlocked)

  def testAPFSUnlockVolumeOnEncryptedAPFS(self):
    """Tests the APFSUnlockVolume function on an encrypted APFS image."""
    resolver.Resolver.key_chain.Empty()

    resolver_context = context.Context()

    test_path = self._GetTestFilePath(['apfs_encrypted.dmg'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    test_tsk_partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/p1',
        parent=test_raw_path_spec)
    test_apfs_container_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, location='/apfs1',
        parent=test_tsk_partition_path_spec)

    container_file_entry = resolver.Resolver.OpenFileEntry(
        test_apfs_container_path_spec, resolver_context=resolver_context)
    fsapfs_volume = container_file_entry.GetAPFSVolume()

    is_unlocked = apfs_helper.APFSUnlockVolume(
        fsapfs_volume, test_apfs_container_path_spec,
        resolver.Resolver.key_chain)
    self.assertFalse(is_unlocked)

    resolver.Resolver.key_chain.SetCredential(
        test_apfs_container_path_spec, 'password', self._APFS_PASSWORD)

    is_unlocked = apfs_helper.APFSUnlockVolume(
        fsapfs_volume, test_apfs_container_path_spec,
        resolver.Resolver.key_chain)
    self.assertTrue(is_unlocked)


if __name__ == '__main__':
  unittest.main()
