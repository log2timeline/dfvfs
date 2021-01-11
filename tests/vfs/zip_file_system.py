#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using the zipfile."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import zip_file_system

from tests import test_lib as shared_test_lib


class ZIPFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests the ZIP file system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['syslog.zip'])
    self._SkipIfPathNotExists(test_path)

    self._os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._zip_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ZIP, location='/',
        parent=self._os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = zip_file_system.ZipFileSystem(
        self._resolver_context, self._zip_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = zip_file_system.ZipFileSystem(
        self._resolver_context, self._zip_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ZIP, location='/syslog',
        parent=self._os_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ZIP, location='/bogus',
        parent=self._os_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    # Test on a zip file that has missing directory entries.
    test_path = self._GetTestFilePath(['missing_directory_entries.zip'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ZIP, location='/',
        parent=test_os_path_spec)

    file_system = zip_file_system.ZipFileSystem(
        self._resolver_context, path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ZIP, location='/folder',
        parent=test_os_path_spec)
    result = file_system.FileEntryExistsByPathSpec(path_spec)
    self.assertTrue(result)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ZIP, location='/folder/syslog',
        parent=test_os_path_spec)
    result = file_system.FileEntryExistsByPathSpec(path_spec)
    self.assertTrue(result)

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = zip_file_system.ZipFileSystem(
        self._resolver_context, self._zip_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ZIP, location='/syslog',
        parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'syslog')

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ZIP, location='/bogus',
        parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    # Test on a tar file that has missing directory entries.
    test_path = self._GetTestFilePath(['missing_directory_entries.zip'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ZIP, location='/',
        parent=test_os_path_spec)

    file_system = zip_file_system.ZipFileSystem(
        self._resolver_context, path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ZIP, location='/folder',
        parent=test_os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsVirtual())
    self.assertEqual(file_entry.name, 'folder')

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ZIP, location='/folder/syslog',
        parent=test_os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'syslog')

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = zip_file_system.ZipFileSystem(
        self._resolver_context, self._zip_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

  # TODO: add tests for GetZipInfoByPathSpec function.


if __name__ == '__main__':
  unittest.main()
