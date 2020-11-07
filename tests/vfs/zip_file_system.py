#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using the zipfile."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import zip_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import zip_file_system

from tests import test_lib as shared_test_lib


class ZIPFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests the ZIP file system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.zip'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._zip_path_spec = zip_path_spec.ZipPathSpec(
        location='/', parent=self._os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = zip_file_system.ZipFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._zip_path_spec)

    file_system.Close()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = zip_file_system.ZipFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._zip_path_spec)

    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = zip_path_spec.ZipPathSpec(
        location='/bogus', parent=self._os_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    file_system.Close()

    # Test on a zip file that has missing directory entries.
    test_file = self._GetTestFilePath(['missing_directory_entries.zip'])
    self._SkipIfPathNotExists(test_file)

    test_file_path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = zip_path_spec.ZipPathSpec(
        location='/', parent=test_file_path_spec)

    file_system = zip_file_system.ZipFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)
    file_system.Open(path_spec)

    path_spec = zip_path_spec.ZipPathSpec(
        location='/folder', parent=test_file_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = zip_path_spec.ZipPathSpec(
        location='/folder/syslog', parent=test_file_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = zip_file_system.ZipFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._zip_path_spec)

    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'syslog')

    path_spec = zip_path_spec.ZipPathSpec(
        location='/bogus', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    file_system.Close()

    # Test on a tar file that has missing directory entries.
    test_file = self._GetTestFilePath(['missing_directory_entries.zip'])
    self._SkipIfPathNotExists(test_file)

    test_file_path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = zip_path_spec.ZipPathSpec(
        location='/', parent=test_file_path_spec)

    file_system = zip_file_system.ZipFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)
    file_system.Open(path_spec)

    path_spec = zip_path_spec.ZipPathSpec(
        location='/folder', parent=test_file_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsVirtual())
    self.assertEqual(file_entry.name, 'folder')

    path_spec = zip_path_spec.ZipPathSpec(
        location='/folder/syslog', parent=test_file_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'syslog')

    file_system.Close()

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = zip_file_system.ZipFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._zip_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    file_system.Close()

  # TODO: add tests for GetZipInfoByPathSpec function.


if __name__ == '__main__':
  unittest.main()
