#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using pybde."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import bde_file_system

from tests import test_lib as shared_test_lib


class BDEFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests the BDE file system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['bdetogo.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._bde_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_BDE, parent=test_os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = bde_file_system.BDEFileSystem(
        self._resolver_context, self._bde_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = bde_file_system.BDEFileSystem(
        self._resolver_context, self._bde_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    result = file_system.FileEntryExistsByPathSpec(self._bde_path_spec)
    self.assertTrue(result)

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = bde_file_system.BDEFileSystem(
        self._resolver_context, self._bde_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    file_entry = file_system.GetFileEntryByPathSpec(self._bde_path_spec)
    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = bde_file_system.BDEFileSystem(
        self._resolver_context, self._bde_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    file_entry = file_system.GetRootFileEntry()
    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')


if __name__ == '__main__':
  unittest.main()
