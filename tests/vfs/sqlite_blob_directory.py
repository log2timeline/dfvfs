#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the directory implementation using SQLite blob."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import sqlite_blob_directory
from dfvfs.vfs import sqlite_blob_file_system

from tests import test_lib as shared_test_lib


class SQLiteBlobDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the SQLite blob directory."""

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
            table_name='myblobs', parent=test_os_path_spec))

    self._file_system = sqlite_blob_file_system.SQLiteBlobFileSystem(
        self._resolver_context, self._sqlite_blob_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = sqlite_blob_directory.SQLiteBlobDirectory(
        self._file_system, self._sqlite_blob_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = sqlite_blob_directory.SQLiteBlobDirectory(
        self._file_system, self._sqlite_blob_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 4)


if __name__ == '__main__':
  unittest.main()
