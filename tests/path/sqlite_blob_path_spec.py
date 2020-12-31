#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the SQLite blob path specification implementation."""

import unittest

from dfvfs.path import sqlite_blob_path_spec

from tests.path import test_lib


class SQLiteBlobPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the SQLite blob path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = sqlite_blob_path_spec.SQLiteBlobPathSpec(
        table_name='test_table', column_name='test_column',
        row_condition=('identifier', '==', 0), parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = sqlite_blob_path_spec.SQLiteBlobPathSpec(
        table_name='test_table', column_name='test_column', row_index=0,
        parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      sqlite_blob_path_spec.SQLiteBlobPathSpec(
          table_name='test_table', column_name='test_column', row_index=0,
          parent=None)

    with self.assertRaises(ValueError):
      sqlite_blob_path_spec.SQLiteBlobPathSpec(
          table_name=None, column_name='test_column', row_index=0,
          parent=self._path_spec)

    with self.assertRaises(ValueError):
      sqlite_blob_path_spec.SQLiteBlobPathSpec(
          table_name='test_table', column_name=None, row_index=0,
          parent=self._path_spec)

    with self.assertRaises(ValueError):
      sqlite_blob_path_spec.SQLiteBlobPathSpec(
          table_name='test_table', column_name='test_column',
          row_condition='identifier == 0', parent=self._path_spec)

    with self.assertRaises(ValueError):
      sqlite_blob_path_spec.SQLiteBlobPathSpec(
          table_name='test_table', column_name='test_column', row_index=0,
          parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = sqlite_blob_path_spec.SQLiteBlobPathSpec(
        table_name='test_table', column_name='test_column',
        row_condition=('identifier', '==', 0), parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        ('type: SQLITE_BLOB, table name: test_table, '
         'column name: test_column, row condition: "identifier == 0"'),
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = sqlite_blob_path_spec.SQLiteBlobPathSpec(
        table_name='test_table', column_name='test_column', row_index=0,
        parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        ('type: SQLITE_BLOB, table name: test_table, '
         'column name: test_column, row index: 0'),
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
