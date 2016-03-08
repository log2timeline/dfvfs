#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using the zipfile."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import zip_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import zip_file_system


class ZipFileSystemTest(unittest.TestCase):
  """The unit test for the zip file system object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'syslog.zip')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._zip_path_spec = zip_path_spec.ZipPathSpec(
        location=u'/', parent=self._os_path_spec)

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = zip_file_system.ZipFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._zip_path_spec)

    file_system.Close()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = zip_file_system.ZipFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._zip_path_spec)

    path_spec = zip_path_spec.ZipPathSpec(
        location=u'/syslog', parent=self._os_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = zip_path_spec.ZipPathSpec(
        location=u'/bogus', parent=self._os_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = zip_file_system.ZipFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._zip_path_spec)

    path_spec = zip_path_spec.ZipPathSpec(
        location=u'/syslog', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, u'syslog')

    path_spec = zip_path_spec.ZipPathSpec(
        location=u'/bogus', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    file_system.Close()

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = zip_file_system.ZipFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._zip_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, u'')

    file_system.Close()


if __name__ == '__main__':
  unittest.main()
