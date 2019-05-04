#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using pyfsapfs."""

from __future__ import unicode_literals

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import apfs_file_system

from tests import test_lib as shared_test_lib


class APFSFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests the APFS file entry."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['apfs.dmg'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    test_tsk_partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/p1',
        parent=test_raw_path_spec)
    self._apfs_container_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, location='/apfs1',
        parent=test_tsk_partition_path_spec)
    self._apfs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS, location='/',
        parent=self._apfs_container_path_spec)

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = apfs_file_system.APFSFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._apfs_path_spec)

    file_system.Close()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = apfs_file_system.APFSFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._apfs_path_spec)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS, location='/passwords.txt',
        identifier=19, parent=self._apfs_container_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS, location='/bogus.txt',
        parent=self._apfs_container_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = apfs_file_system.APFSFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._apfs_path_spec)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS, identifier=19,
        parent=self._apfs_container_path_spec)

    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    # There is no way to determine the file_entry.name without a location string
    # in the path_spec or retrieving the file_entry from its parent.

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS, location='/passwords.txt',
        identifier=19, parent=self._apfs_container_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'passwords.txt')

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS, location='/bogus.txt',
        parent=self._apfs_container_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    file_system.Close()

  # TODO: add tests for GetAPFSFileEntryByPathSpec function.

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = apfs_file_system.APFSFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._apfs_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    file_system.Close()


if __name__ == '__main__':
  unittest.main()
