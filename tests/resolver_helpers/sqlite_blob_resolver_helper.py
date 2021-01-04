#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the sqlite blob file resolver helper implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver_helpers import sqlite_blob_resolver_helper

from tests.resolver_helpers import test_lib


class SQLiteBlobResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the sqlite blob resolver helper implementation."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(SQLiteBlobResolverHelperTest, self).setUp()

    test_path = self._GetTestFilePath(['blob.db'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._sqlite_blob_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_SQLITE_BLOB, table_name='myblobs',
        column_name='blobs', row_condition=('name', '==', 'mmssms.db'),
        parent=test_os_path_spec)

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = (
        sqlite_blob_resolver_helper.SQLiteBlobResolverHelper())
    self._TestNewFileObject(resolver_helper_object, self._sqlite_blob_path_spec)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = (
        sqlite_blob_resolver_helper.SQLiteBlobResolverHelper())
    self._TestNewFileSystem(resolver_helper_object, self._sqlite_blob_path_spec)


if __name__ == '__main__':
  unittest.main()
