#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using the SleuthKit (TSK)."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import tsk_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import tsk_file_system


class TSKFileSystemTest(unittest.TestCase):
  """The unit test for the SleuthKit (TSK) file system object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'ímynd.dd')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._tsk_path_spec = tsk_path_spec.TSKPathSpec(
        location=u'/', parent=self._os_path_spec)

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = tsk_file_system.TSKFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._tsk_path_spec)

    file_system.Close()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = tsk_file_system.TSKFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._tsk_path_spec)

    path_spec = tsk_path_spec.TSKPathSpec(
        inode=15, location=u'/password.txt', parent=self._os_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = tsk_path_spec.TSKPathSpec(
        inode=19, location=u'/bogus.txt', parent=self._os_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = tsk_file_system.TSKFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._tsk_path_spec)

    path_spec = tsk_path_spec.TSKPathSpec(inode=15, parent=self._os_path_spec)

    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    # There is no way to determine the file_entry.name without a location string
    # in the path_spec or retrieving the file_entry from its parent.

    path_spec = tsk_path_spec.TSKPathSpec(
        inode=15, location=u'/password.txt', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, u'password.txt')

    path_spec = tsk_path_spec.TSKPathSpec(
        inode=19, location=u'/bogus.txt', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    file_system.Close()

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = tsk_file_system.TSKFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._tsk_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, u'')

    file_system.Close()


if __name__ == '__main__':
  unittest.main()
