#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using sqlite blob."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import sqlite_blob_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import sqlite_blob_file_system

from tests import test_lib as shared_test_lib


class SQLiteBlobFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests for the sqlite blob file system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['blob.db'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._sqlite_blob_path_spec = sqlite_blob_path_spec.SQLiteBlobPathSpec(
        table_name='myblobs', column_name='blobs',
        row_condition=('name', '==', 'mmssms.db'), parent=path_spec)
    self._sqlite_blob_path_spec_2 = sqlite_blob_path_spec.SQLiteBlobPathSpec(
        table_name='myblobs', column_name='blobs',
        row_index=2, parent=path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = sqlite_blob_file_system.SQLiteBlobFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._sqlite_blob_path_spec)

    file_system.Close()

    file_system.Open(self._sqlite_blob_path_spec_2)

    file_system.Close()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = sqlite_blob_file_system.SQLiteBlobFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._sqlite_blob_path_spec)

    self.assertTrue(file_system.FileEntryExistsByPathSpec(
        self._sqlite_blob_path_spec))

    self.assertTrue(file_system.FileEntryExistsByPathSpec(
        self._sqlite_blob_path_spec_2))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = sqlite_blob_file_system.SQLiteBlobFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._sqlite_blob_path_spec)

    file_entry = file_system.GetFileEntryByPathSpec(self._sqlite_blob_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'WHERE name == \'mmssms.db\'')

    file_entry = file_system.GetFileEntryByPathSpec(
        self._sqlite_blob_path_spec_2)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'OFFSET 2')

    file_system.Close()

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = sqlite_blob_file_system.SQLiteBlobFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._sqlite_blob_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'myblobs.blobs')

    file_system.Close()


if __name__ == '__main__':
  unittest.main()
