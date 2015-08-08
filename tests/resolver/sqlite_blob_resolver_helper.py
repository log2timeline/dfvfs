#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the sqlite blob file resolver helper implementation."""

import unittest

from dfvfs.resolver import sqlite_blob_resolver_helper
from tests.resolver import test_lib


class SqliteBlobResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the sqlite blob resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = (
        sqlite_blob_resolver_helper.SqliteBlobResolverHelper())
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = (
        sqlite_blob_resolver_helper.SqliteBlobResolverHelper())
    self._TestNewFileSystem(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
