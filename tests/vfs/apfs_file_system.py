#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using pyfsapfs."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import apfs_container_path_spec
from dfvfs.path import apfs_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import raw_path_spec
from dfvfs.path import tsk_partition_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import apfs_file_system

from tests import test_lib as shared_test_lib


@shared_test_lib.skipUnlessHasTestFile(['apfs.dmg'])
class APFSFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests the APFS file entry."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['apfs.dmg'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)
    partition_path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p1', parent=path_spec)
    self._apfs_container_path_spec = (
        apfs_container_path_spec.APFSContainerPathSpec(
            location='/apfs1', parent=partition_path_spec))
    self._apfs_path_spec = apfs_path_spec.APFSPathSpec(
        location='/', parent=self._apfs_container_path_spec)

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

    path_spec = apfs_path_spec.APFSPathSpec(
        location='/passwords.txt', identifier=19,
        parent=self._apfs_container_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = apfs_path_spec.APFSPathSpec(
        location='/bogus.txt', parent=self._apfs_container_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = apfs_file_system.APFSFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._apfs_path_spec)

    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=19, parent=self._apfs_container_path_spec)

    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    # There is no way to determine the file_entry.name without a location string
    # in the path_spec or retrieving the file_entry from its parent.

    path_spec = apfs_path_spec.APFSPathSpec(
        location='/passwords.txt', identifier=19,
        parent=self._apfs_container_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'passwords.txt')

    path_spec = apfs_path_spec.APFSPathSpec(
        location='/bogus.txt', parent=self._apfs_container_path_spec)
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
