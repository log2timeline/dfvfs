#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using SQLite blob."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import sqlite_blob_file_entry
from dfvfs.vfs import sqlite_blob_file_system

from tests import test_lib as shared_test_lib


class SQLiteBlobFileEntryTest(shared_test_lib.BaseTestCase):
  """Tests for the SQLite blob file entry."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['blob.db'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._sqlite_blob_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_SQLITE_BLOB, column_name='blobs',
        parent=test_os_path_spec, row_condition=('name', '==', 'mmssms.db'),
        table_name='myblobs')
    self._sqlite_blob_path_spec_2 = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_SQLITE_BLOB, column_name='blobs',
        parent=test_os_path_spec, row_index=2, table_name='myblobs')
    self._sqlite_blob_path_spec_3 = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_SQLITE_BLOB, column_name='blobs',
        parent=test_os_path_spec, row_condition=('name', '==', 4),
        table_name='myblobs')
    self._sqlite_blob_path_spec_directory = (
        path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_SQLITE_BLOB, column_name='blobs',
            parent=test_os_path_spec, table_name='myblobs'))

    self._file_system = sqlite_blob_file_system.SQLiteBlobFileSystem(
        self._resolver_context, self._sqlite_blob_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testIntialize(self):
    """Test the __init__ function."""
    file_entry = sqlite_blob_file_entry.SQLiteBlobFileEntry(
        self._resolver_context, self._file_system, self._sqlite_blob_path_spec)

    self.assertIsNotNone(file_entry)

    file_entry = sqlite_blob_file_entry.SQLiteBlobFileEntry(
        self._resolver_context, self._file_system,
        self._sqlite_blob_path_spec_2)

    self.assertIsNotNone(file_entry)

  # TODO: add tests for _GetDirectory
  # TODO: add tests for _GetSubFileEntries

  def testName(self):
    """Test name property."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._sqlite_blob_path_spec)
    self.assertTrue(file_entry.name == (
        'WHERE name == \'mmssms.db\''))

    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._sqlite_blob_path_spec_3)
    self.assertTrue(file_entry.name == 'WHERE name == 4')

    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._sqlite_blob_path_spec_directory)
    self.assertTrue(file_entry.name == 'myblobs.blobs')

  def testSize(self):
    """Test the size property."""
    file_entry = sqlite_blob_file_entry.SQLiteBlobFileEntry(
        self._resolver_context, self._file_system, self._sqlite_blob_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 110592)

  # TODO: add tests for GetNumberOfRows

  def testGetFileEntryByPathSpec(self):
    """Test the get a file entry by path specification functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._sqlite_blob_path_spec)

    self.assertIsNotNone(file_entry)

    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._sqlite_blob_path_spec_2)

    self.assertIsNotNone(file_entry)

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._sqlite_blob_path_spec)

    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, 'myblobs.blobs')

  def testIsFunctions(self):
    """Test the Is? functions."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._sqlite_blob_path_spec)

    self.assertFalse(file_entry.IsRoot())
    self.assertFalse(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertFalse(file_entry.IsDirectory())
    self.assertTrue(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

  def testSubFileEntries(self):
    """Test the sub file entries iteration functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._sqlite_blob_path_spec_directory)

    self.assertTrue(file_entry.IsDirectory())

    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 4)

    expected_sub_file_entry_names = [
        'OFFSET 0', 'OFFSET 1', 'OFFSET 2', 'OFFSET 3']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), expected_sub_file_entry_names)


if __name__ == '__main__':
  unittest.main()
