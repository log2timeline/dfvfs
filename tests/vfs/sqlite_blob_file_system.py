#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using sqlite blob."""

import os
import unittest

from dfvfs.path import sqlite_blob_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import sqlite_blob_file_system


class SQLiteBlobFileSystemTest(unittest.TestCase):
  """The unit test for the sqlite blob file system object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'blob.db')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._sqlite_blob_path_spec = sqlite_blob_path_spec.SQLiteBlobPathSpec(
        table_name=u'myblobs', column_name=u'blobs',
        row_condition=(u'name', u'==', u'mmssms.db'), parent=path_spec)
    self._sqlite_blob_path_spec_2 = sqlite_blob_path_spec.SQLiteBlobPathSpec(
        table_name=u'myblobs', column_name=u'blobs',
        row_index=2, parent=path_spec)

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
    self.assertEqual(file_entry.name, u'WHERE name == \'mmssms.db\'')

    file_entry = file_system.GetFileEntryByPathSpec(
        self._sqlite_blob_path_spec_2)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, u'OFFSET 2')

    file_system.Close()

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = sqlite_blob_file_system.SQLiteBlobFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._sqlite_blob_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, u'myblobs.blobs')

    file_system.Close()


if __name__ == '__main__':
  unittest.main()
