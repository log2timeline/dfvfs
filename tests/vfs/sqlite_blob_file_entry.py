#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using SQLite blob."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import sqlite_blob_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import sqlite_blob_file_entry
from dfvfs.vfs import sqlite_blob_file_system

from tests import test_lib as shared_test_lib


class SQLiteBlobDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the SQLite blob directory."""

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
    self._sqlite_blob_path_spec_3 = sqlite_blob_path_spec.SQLiteBlobPathSpec(
        table_name='myblobs', column_name='blobs',
        row_condition=('name', '==', 4), parent=path_spec)
    self._sqlite_blob_path_spec_directory = (
        sqlite_blob_path_spec.SQLiteBlobPathSpec(
            table_name='myblobs', column_name='blobs', parent=path_spec))

    self._file_system = sqlite_blob_file_system.SQLiteBlobFileSystem(
        self._resolver_context)
    self._file_system.Open(self._sqlite_blob_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = sqlite_blob_file_entry.SQLiteBlobDirectory(
        self._file_system, self._sqlite_blob_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = sqlite_blob_file_entry.SQLiteBlobDirectory(
        self._file_system, self._sqlite_blob_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 4)


class SQLiteBlobFileEntryTest(shared_test_lib.BaseTestCase):
  """Tests for the SQLite blob file entry."""

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
    self._sqlite_blob_path_spec_3 = sqlite_blob_path_spec.SQLiteBlobPathSpec(
        table_name='myblobs', column_name='blobs',
        row_condition=('name', '==', 4), parent=path_spec)
    self._sqlite_blob_path_spec_directory = (
        sqlite_blob_path_spec.SQLiteBlobPathSpec(
            table_name='myblobs', column_name='blobs', parent=path_spec))

    self._file_system = sqlite_blob_file_system.SQLiteBlobFileSystem(
        self._resolver_context)
    self._file_system.Open(self._sqlite_blob_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
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

  def testGetStat(self):
    """Tests the GetStat function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._sqlite_blob_path_spec)

    stat_object = file_entry.GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 110592)

    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._sqlite_blob_path_spec_2)

    stat_object = file_entry.GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 11)

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
