#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the APFS container file system implementation using pyfsapfs."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import apfs_container_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import raw_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import apfs_container_file_system

from tests import test_lib as shared_test_lib


class APFSContainerFileSystemTest(shared_test_lib.BaseTestCase):
  """APFS container file system tests."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['apfs.raw'])
    self._SkipIfPathNotExists(test_file)

    test_os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._raw_path_spec = raw_path_spec.RawPathSpec(parent=test_os_path_spec)
    self._apfs_container_path_spec = (
        apfs_container_path_spec.APFSContainerPathSpec(
            location='/', parent=self._raw_path_spec))

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = apfs_container_file_system.APFSContainerFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._apfs_container_path_spec)

    file_system.Close()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = apfs_container_file_system.APFSContainerFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._apfs_container_path_spec)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/', parent=self._raw_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        parent=self._raw_path_spec, volume_index=0)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/apfs1', parent=self._raw_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        parent=self._raw_path_spec, volume_index=9)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/apfs0', parent=self._raw_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/apfs9', parent=self._raw_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = apfs_container_file_system.APFSContainerFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._apfs_container_path_spec)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/', parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        parent=self._raw_path_spec, volume_index=0)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'apfs1')

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/apfs1', parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'apfs1')

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        parent=self._raw_path_spec, volume_index=9)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/apfs0', parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/apfs9', parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    file_system.Close()

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = apfs_container_file_system.APFSContainerFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._apfs_container_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    file_system.Close()

  # TODO: add tests for GetAPFSVolumeByPathSpec function.


if __name__ == '__main__':
  unittest.main()
