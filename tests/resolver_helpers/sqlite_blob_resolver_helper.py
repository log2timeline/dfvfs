#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the sqlite blob file resolver helper implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.resolver_helpers import sqlite_blob_resolver_helper

from tests.resolver_helpers import test_lib


class SQLiteBlobResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the sqlite blob resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = (
        sqlite_blob_resolver_helper.SQLiteBlobResolverHelper())
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = (
        sqlite_blob_resolver_helper.SQLiteBlobResolverHelper())
    self._TestNewFileSystem(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
