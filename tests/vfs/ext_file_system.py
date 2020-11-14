#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using pyfsext."""

from __future__ import unicode_literals

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import ext_file_system

from tests import test_lib as shared_test_lib


class EXTFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests the EXT file entry."""

  _INODE_PASSWORD_TXT = 20

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['ext2.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, location='/',
        parent=self._raw_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = ext_file_system.EXTFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._ext_path_spec)

    file_system.Close()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = ext_file_system.EXTFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._ext_path_spec)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, location='/passwords.txt',
        inode=self._INODE_PASSWORD_TXT, parent=self._raw_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, location='/bogus.txt',
        parent=self._raw_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = ext_file_system.EXTFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._ext_path_spec)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, inode=self._INODE_PASSWORD_TXT,
        parent=self._raw_path_spec)

    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    # There is no way to determine the file_entry.name without a location string
    # in the path_spec or retrieving the file_entry from its parent.

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, location='/passwords.txt',
        inode=self._INODE_PASSWORD_TXT, parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'passwords.txt')

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, location='/bogus.txt',
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    file_system.Close()

  # TODO: add tests for GetEXTFileEntryByPathSpec function.

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = ext_file_system.EXTFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._ext_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    file_system.Close()


if __name__ == '__main__':
  unittest.main()
