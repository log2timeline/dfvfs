#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the SQLite blob file-like object."""

from __future__ import unicode_literals

import unittest

from dfvfs.file_io import sqlite_blob_file_io
from dfvfs.path import sqlite_blob_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context

from tests.file_io import test_lib


class SQLiteBlobFileWithConditionTest(test_lib.SylogTestCase):
  """The unit test for a SQLite blob file-like object using row condition."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.db'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._sqlite_blob_path_spec = sqlite_blob_path_spec.SQLiteBlobPathSpec(
        table_name='blobs', column_name='blob',
        row_condition=('identifier', '==', 'myblob'), parent=path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = sqlite_blob_file_io.SQLiteBlobFile(self._resolver_context)
    file_object.open(path_spec=self._sqlite_blob_path_spec)

    self._TestGetSizeFileObject(file_object)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = sqlite_blob_file_io.SQLiteBlobFile(self._resolver_context)
    file_object.open(path_spec=self._sqlite_blob_path_spec)

    self._TestSeekFileObject(file_object)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = sqlite_blob_file_io.SQLiteBlobFile(self._resolver_context)
    file_object.open(path_spec=self._sqlite_blob_path_spec)

    self._TestReadFileObject(file_object)

    file_object.close()


class SQLiteBlobFileWithIndexTest(test_lib.SylogTestCase):
  """The unit test for a SQLite blob file-like object using row index."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.db'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._sqlite_blob_path_spec = sqlite_blob_path_spec.SQLiteBlobPathSpec(
        table_name='blobs', column_name='blob', row_index=0, parent=path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = sqlite_blob_file_io.SQLiteBlobFile(self._resolver_context)
    file_object.open(path_spec=self._sqlite_blob_path_spec)

    self._TestGetSizeFileObject(file_object)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = sqlite_blob_file_io.SQLiteBlobFile(self._resolver_context)
    file_object.open(path_spec=self._sqlite_blob_path_spec)

    self._TestSeekFileObject(file_object)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = sqlite_blob_file_io.SQLiteBlobFile(self._resolver_context)
    file_object.open(path_spec=self._sqlite_blob_path_spec)

    self._TestReadFileObject(file_object)

    file_object.close()


if __name__ == '__main__':
  unittest.main()
