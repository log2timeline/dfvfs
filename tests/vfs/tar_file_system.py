#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using the tarfile."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import tar_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import tar_file_system

from tests import test_lib as shared_test_lib


class TARFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests the TAR file system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.tar'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._tar_path_spec = tar_path_spec.TARPathSpec(
        location='/syslog', parent=self._os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = tar_file_system.TARFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._tar_path_spec)

    file_system.Close()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = tar_file_system.TARFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._tar_path_spec)

    path_spec = tar_path_spec.TARPathSpec(
        location='/syslog', parent=self._os_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = tar_path_spec.TARPathSpec(
        location='/bogus', parent=self._os_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    file_system.Close()

    # Test on a tar file that has missing directory entries.
    test_file = self._GetTestFilePath(['missing_directory_entries.tar'])
    self._SkipIfPathNotExists(test_file)

    test_file_path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = tar_path_spec.TARPathSpec(
        location='/', parent=test_file_path_spec)

    file_system = tar_file_system.TARFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)
    file_system.Open(path_spec)

    path_spec = tar_path_spec.TARPathSpec(
        location='/File System', parent=test_file_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = tar_path_spec.TARPathSpec(
        location='/File System/Recordings', parent=test_file_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = tar_file_system.TARFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._tar_path_spec)

    path_spec = tar_path_spec.TARPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'syslog')

    path_spec = tar_path_spec.TARPathSpec(
        location='/bogus', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    file_system.Close()

    # Test on a tar file that has missing directory entries.
    test_file = self._GetTestFilePath(['missing_directory_entries.tar'])
    self._SkipIfPathNotExists(test_file)

    test_file_path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = tar_path_spec.TARPathSpec(
        location='/', parent=test_file_path_spec)

    file_system = tar_file_system.TARFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)
    file_system.Open(path_spec)

    path_spec = tar_path_spec.TARPathSpec(
        location='/File System', parent=test_file_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'File System')

    path_spec = tar_path_spec.TARPathSpec(
        location='/File System/Recordings', parent=test_file_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'Recordings')

    file_system.Close()

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = tar_file_system.TARFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._tar_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    file_system.Close()


if __name__ == '__main__':
  unittest.main()
