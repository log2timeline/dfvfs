#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the APFS container file system implementation using pyfsapfs."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import apfs_container_file_system

from tests import test_lib as shared_test_lib


class APFSContainerFileSystemTest(shared_test_lib.BaseTestCase):
  """APFS container file system tests."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['apfs.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._apfs_container_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, location='/',
        parent=self._raw_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  # fsapfsinfo apfs.raw
  #
  # Apple File System (APFS) information:
  #
  # Container information:
  #   Identifier                    : d08a9fa0-d5a5-458b-813e-ebf9bf5d5338
  #   Number of volumes             : 1
  #
  # Volume: 1 information:
  #   Identifier                    : 458ed10d-8ac3-4af1-8dfd-3954d151a3f3
  #   Name                          : apfs_test
  #   Compatible features           : 0x00000002
  #         (NX_FEATURE_LCFD)
  #
  #   Incompatible features         : 0x00000001
  #         (NX_INCOMPAT_VERSION1)
  #
  #   Read-only compatible features : 0x00000000
  #
  #   Number of snapshots           : 0

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = apfs_container_file_system.APFSContainerFileSystem(
        self._resolver_context, self._apfs_container_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = apfs_container_file_system.APFSContainerFileSystem(
        self._resolver_context, self._apfs_container_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, location='/',
        parent=self._raw_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, parent=self._raw_path_spec,
        volume_index=0)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, location='/apfs1',
        parent=self._raw_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER,
        location='/apfs{458ed10d-8ac3-4af1-8dfd-3954d151a3f3}',
        parent=self._raw_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, parent=self._raw_path_spec,
        volume_index=9)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, location='/apfs0',
        parent=self._raw_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, location='/apfs9',
        parent=self._raw_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

  # TODO: add tests for GetAPFSVolumeByPathSpec function.

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = apfs_container_file_system.APFSContainerFileSystem(
        self._resolver_context, self._apfs_container_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, location='/',
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, parent=self._raw_path_spec,
        volume_index=0)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'apfs1')

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, location='/apfs1',
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'apfs1')

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER,
        location='/apfs{458ed10d-8ac3-4af1-8dfd-3954d151a3f3}',
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'apfs1')

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, parent=self._raw_path_spec,
        volume_index=9)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, location='/apfs0',
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, location='/apfs9',
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = apfs_container_file_system.APFSContainerFileSystem(
        self._resolver_context, self._apfs_container_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

  def testGetVolumeIndexByPathSpec(self):
    """Tests the GetVolumeIndexByPathSpec function."""
    file_system = apfs_container_file_system.APFSContainerFileSystem(
        self._resolver_context, self._apfs_container_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER,
        parent=self._raw_path_spec)

    self.assertIsNotNone(path_spec)

    volume_index = file_system.GetVolumeIndexByPathSpec(path_spec)
    self.assertIsNone(volume_index)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER,
        location='/apfs1', parent=self._raw_path_spec)

    self.assertIsNotNone(path_spec)

    volume_index = file_system.GetVolumeIndexByPathSpec(path_spec)
    self.assertEqual(volume_index, 0)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER,
        location='/apfs{458ed10d-8ac3-4af1-8dfd-3954d151a3f3}',
        parent=self._raw_path_spec)

    self.assertIsNotNone(path_spec)

    volume_index = file_system.GetVolumeIndexByPathSpec(path_spec)
    self.assertEqual(volume_index, 0)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER,
        parent=self._raw_path_spec, volume_index=0)

    self.assertIsNotNone(path_spec)

    volume_index = file_system.GetVolumeIndexByPathSpec(path_spec)
    self.assertEqual(volume_index, 0)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER,
        location='/apfs1', parent=self._raw_path_spec, volume_index=0)

    self.assertIsNotNone(path_spec)

    volume_index = file_system.GetVolumeIndexByPathSpec(path_spec)
    self.assertEqual(volume_index, 0)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER,
        location='/apfs', parent=self._raw_path_spec)

    volume_index = file_system.GetVolumeIndexByPathSpec(path_spec)
    self.assertIsNone(volume_index)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER,
        location='/apfs101', parent=self._raw_path_spec)

    volume_index = file_system.GetVolumeIndexByPathSpec(path_spec)
    self.assertIsNone(volume_index)


if __name__ == '__main__':
  unittest.main()
