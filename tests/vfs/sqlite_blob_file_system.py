#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using sqlite blob."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import sqlite_blob_file_system

from tests import test_lib as shared_test_lib


class SQLiteBlobFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests for the sqlite blob file system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['blob.db'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._sqlite_blob_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_SQLITE_BLOB, table_name='myblobs',
        column_name='blobs', row_condition=('name', '==', 'mmssms.db'),
        parent=test_os_path_spec)

    self._sqlite_blob_path_spec_2 = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_SQLITE_BLOB, table_name='myblobs',
        column_name='blobs', row_index=2, parent=test_os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = sqlite_blob_file_system.SQLiteBlobFileSystem(
        self._resolver_context, self._sqlite_blob_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    file_system = sqlite_blob_file_system.SQLiteBlobFileSystem(
        self._resolver_context, self._sqlite_blob_path_spec_2)
    self.assertIsNotNone(file_system)

    file_system.Open()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = sqlite_blob_file_system.SQLiteBlobFileSystem(
        self._resolver_context, self._sqlite_blob_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    result = file_system.FileEntryExistsByPathSpec(self._sqlite_blob_path_spec)
    self.assertTrue(result)

    result = file_system.FileEntryExistsByPathSpec(
        self._sqlite_blob_path_spec_2)
    self.assertTrue(result)

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = sqlite_blob_file_system.SQLiteBlobFileSystem(
        self._resolver_context, self._sqlite_blob_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    file_entry = file_system.GetFileEntryByPathSpec(self._sqlite_blob_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'WHERE name == \'mmssms.db\'')

    file_entry = file_system.GetFileEntryByPathSpec(
        self._sqlite_blob_path_spec_2)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'OFFSET 2')

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = sqlite_blob_file_system.SQLiteBlobFileSystem(
        self._resolver_context, self._sqlite_blob_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'myblobs.blobs')


if __name__ == '__main__':
  unittest.main()
