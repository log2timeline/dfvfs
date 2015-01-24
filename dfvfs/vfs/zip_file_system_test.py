#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using the zipfile."""

import os
import unittest

from dfvfs.file_io import os_file_io
from dfvfs.path import os_path_spec
from dfvfs.path import zip_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import zip_file_system


class ZipFileSystemTest(unittest.TestCase):
  """The unit test for the zip file system object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join('test_data', 'syslog.zip')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._os_file_object = os_file_io.OSFile(self._resolver_context)
    self._os_file_object.open(self._os_path_spec, mode='rb')

  def testIntialize(self):
    """Test the initialize functionality."""
    file_system = zip_file_system.ZipFileSystem(
        self._resolver_context, self._os_file_object, self._os_path_spec)

    self.assertNotEquals(file_system, None)

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = zip_file_system.ZipFileSystem(
        self._resolver_context, self._os_file_object, self._os_path_spec)

    path_spec = zip_path_spec.ZipPathSpec(
        location=u'/syslog', parent=self._os_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = zip_path_spec.ZipPathSpec(
        location=u'/bogus', parent=self._os_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

  def testGetFileEntryByPathSpec(self):
    """Test the get entry by path specification functionality."""
    file_system = zip_file_system.ZipFileSystem(
        self._resolver_context, self._os_file_object, self._os_path_spec)

    path_spec = zip_path_spec.ZipPathSpec(
        location=u'/syslog', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)
    self.assertEquals(file_entry.name, u'syslog')

    path_spec = zip_path_spec.ZipPathSpec(
        location=u'/bogus', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertEquals(file_entry, None)

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = zip_file_system.ZipFileSystem(
        self._resolver_context, self._os_file_object, self._os_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertNotEquals(file_entry, None)
    self.assertEquals(file_entry.name, u'')

if __name__ == '__main__':
  unittest.main()
