#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using the tarfile."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import tar_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import tar_file_system


class TarFileSystemTest(unittest.TestCase):
  """The unit test for the tar file system object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'syslog.tar')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._tar_path_spec = tar_path_spec.TarPathSpec(
        location=u'/syslog', parent=self._os_path_spec)

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = tar_file_system.TarFileSystem(self._resolver_context)
    self.assertNotEqual(file_system, None)

    file_system.Open(self._tar_path_spec)

    file_system.Close()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = tar_file_system.TarFileSystem(self._resolver_context)
    self.assertNotEqual(file_system, None)

    file_system.Open(self._tar_path_spec)

    path_spec = tar_path_spec.TarPathSpec(
        location=u'/syslog', parent=self._os_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = tar_path_spec.TarPathSpec(
        location=u'/bogus', parent=self._os_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Test the get entry by path specification functionality."""
    file_system = tar_file_system.TarFileSystem(self._resolver_context)
    self.assertNotEqual(file_system, None)

    file_system.Open(self._tar_path_spec)

    path_spec = tar_path_spec.TarPathSpec(
        location=u'/syslog', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEqual(file_entry, None)
    self.assertEqual(file_entry.name, u'syslog')

    path_spec = tar_path_spec.TarPathSpec(
        location=u'/bogus', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertEqual(file_entry, None)

    file_system.Close()

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = tar_file_system.TarFileSystem(self._resolver_context)
    self.assertNotEqual(file_system, None)

    file_system.Open(self._tar_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertNotEqual(file_entry, None)
    self.assertEqual(file_entry.name, u'')

    file_system.Close()


if __name__ == '__main__':
  unittest.main()
