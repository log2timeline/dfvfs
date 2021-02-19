#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the SQLite blob file-like object."""

import unittest

from dfvfs.file_io import sqlite_blob_file_io
from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context

from tests.file_io import test_lib


class SQLiteBlobFileWithConditionTest(test_lib.SylogTestCase):
  """The unit test for a SQLite blob file-like object using row condition."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['syslog.db'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._sqlite_blob_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_SQLITE_BLOB, column_name='blob',
        parent=test_os_path_spec, row_condition=('identifier', '==', 'myblob'),
        table_name='blobs')

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = sqlite_blob_file_io.SQLiteBlobFile(
        self._resolver_context, self._sqlite_blob_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    file_object = sqlite_blob_file_io.SQLiteBlobFile(
        self._resolver_context, self._sqlite_blob_path_spec)
    file_object.Open()

    self._TestSeekFileObject(file_object)

  def testRead(self):
    """Test the read functionality."""
    file_object = sqlite_blob_file_io.SQLiteBlobFile(
        self._resolver_context, self._sqlite_blob_path_spec)
    file_object.Open()

    self._TestReadFileObject(file_object)


class SQLiteBlobFileWithIndexTest(test_lib.SylogTestCase):
  """The unit test for a SQLite blob file-like object using row index."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['syslog.db'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._sqlite_blob_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_SQLITE_BLOB, column_name='blob',
        parent=test_os_path_spec, row_index=0, table_name='blobs')

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = sqlite_blob_file_io.SQLiteBlobFile(
        self._resolver_context, self._sqlite_blob_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    file_object = sqlite_blob_file_io.SQLiteBlobFile(
        self._resolver_context, self._sqlite_blob_path_spec)
    file_object.Open()

    self._TestSeekFileObject(file_object)

  def testRead(self):
    """Test the read functionality."""
    file_object = sqlite_blob_file_io.SQLiteBlobFile(
        self._resolver_context, self._sqlite_blob_path_spec)
    file_object.Open()

    self._TestReadFileObject(file_object)


if __name__ == '__main__':
  unittest.main()
