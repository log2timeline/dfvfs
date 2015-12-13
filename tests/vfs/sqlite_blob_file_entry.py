#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using sqlite blob."""

import os
import unittest

from dfvfs.path import sqlite_blob_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import sqlite_blob_file_entry
from dfvfs.vfs import sqlite_blob_file_system


class SqliteBlobFileEntryTest(unittest.TestCase):
  """The unit test for the sqlite blob file entry object."""

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

    self._file_system = sqlite_blob_file_system.SQLiteBlobFileSystem(
        self._resolver_context)
    self._file_system.Open(self._sqlite_blob_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()

  def testIntialize(self):
    """Test the initialize functionality."""
    file_entry = sqlite_blob_file_entry.SQLiteBlobFileEntry(
        self._resolver_context, self._file_system, self._sqlite_blob_path_spec)

    self.assertNotEqual(file_entry, None)

    file_entry = sqlite_blob_file_entry.SQLiteBlobFileEntry(
        self._resolver_context, self._file_system,
        self._sqlite_blob_path_spec_2)

    self.assertNotEqual(file_entry, None)

  def testGetFileEntryByPathSpec(self):
    """Test the get a file entry by path specification functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._sqlite_blob_path_spec)

    self.assertNotEqual(file_entry, None)

    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._sqlite_blob_path_spec_2)

    self.assertNotEqual(file_entry, None)

  def testGetParentFileEntry(self):
    """Test the get parent file entry functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._sqlite_blob_path_spec)

    self.assertNotEqual(file_entry, None)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertNotEqual(parent_file_entry, None)

    self.assertEqual(parent_file_entry.name, u'myblobs.blobs')

  def testGetStat(self):
    """Test the get stat functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._sqlite_blob_path_spec)

    stat_object = file_entry.GetStat()

    self.assertNotEqual(stat_object, None)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 110592)

    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._sqlite_blob_path_spec_2)

    stat_object = file_entry.GetStat()

    self.assertNotEqual(stat_object, None)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 11)

  def testIsFunctions(self):
    """Test the Is? functionality."""
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
        self._sqlite_blob_path_spec)

    self.assertNotEqual(file_entry, None)

    self.assertEqual(file_entry.number_of_sub_file_entries, 4)

    expected_sub_file_entry_names = [
        u'OFFSET 0', u'OFFSET 1', u'OFFSET 2', u'OFFSET 3']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), expected_sub_file_entry_names)


if __name__ == '__main__':
  unittest.main()
