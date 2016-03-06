#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the operating system file system implementation."""

import os
import platform
import unittest

from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import os_file_system


def TestPlatformSystem():
  """Test function to emulate platform.system() == 'Windows'"""
  return u'Windows'


class OSFileSystemTest(unittest.TestCase):
  """The unit test for the operating system file system object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def testIntialize(self):
    """Test the intialize functionality."""
    file_system = os_file_system.OSFileSystem(self._resolver_context)

    self.assertIsNotNone(file_system)

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = os_file_system.OSFileSystem(self._resolver_context)

    path_spec = os_path_spec.OSPathSpec(
        location=os.path.join(u'test_data', u'testdir_os', u'file1.txt'))
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = os_path_spec.OSPathSpec(
        location=os.path.join(u'test_data', u'testdir_os', u'file6.txt'))
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = os_file_system.OSFileSystem(self._resolver_context)

    path_spec = os_path_spec.OSPathSpec(
        location=os.path.join(u'test_data', u'testdir_os', u'file1.txt'))
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, u'file1.txt')

    path_spec = os_path_spec.OSPathSpec(
        location=os.path.join(u'test_data', u'testdir_os', u'file6.txt'))
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = os_file_system.OSFileSystem(self._resolver_context)

    if platform.system() == u'Windows':
      # Return the root with the drive letter of the volume the current
      # working directory is on.
      expected_location = os.getcwd()
      expected_location, _, _ = expected_location.partition(u'\\')
    else:
      expected_location = u''

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, expected_location)

  def testJoinPathWindows(self):
    """Test the join path functionality for Windows."""
    # In this test we emulate we are running on Windows.
    original_platform_system = platform.system
    platform.system = TestPlatformSystem

    file_system = os_file_system.OSFileSystem(self._resolver_context)
    file_system.PATH_SEPARATOR = u'\\'

    expected_path = u'\\\\.\\PhysicalDrive0'

    path = file_system.JoinPath([u'\\\\.\\PhysicalDrive0'])
    self.assertEqual(path, expected_path)

    expected_path = u'\\\\.\\C:'

    path = file_system.JoinPath([u'\\\\.\\C:'])
    self.assertEqual(path, expected_path)

    expected_path = u'C:'

    path = file_system.JoinPath([u'\\\\.\\C:\\'])
    self.assertEqual(path, expected_path)

    expected_path = (
        u'\\\\?\\Volume{26a21bda-a627-11d7-9931-806e6f6e6963}\\test1')

    path = file_system.JoinPath([
        u'\\\\?\\Volume{26a21bda-a627-11d7-9931-806e6f6e6963}\\', u'test1'])
    self.assertEqual(path, expected_path)

    expected_path = u'C:\\test1\\test2\\test3'

    path = file_system.JoinPath([u'C:', u'test1', u'test2', u'test3'])
    self.assertEqual(path, expected_path)

    path = file_system.JoinPath([
        u'C:\\', u'test1\\\\', u'\\\\test2', u'test3\\'])
    self.assertEqual(path, expected_path)

    path = file_system.JoinPath([u'C:\\test1\\\\', u'\\\\test2\\test3'])
    self.assertEqual(path, expected_path)

    path = file_system.JoinPath([u'\\\\.\\C:\\', u'test1', u'test2', u'test3'])
    self.assertEqual(path, expected_path)

    expected_path = u'\\\\server\\share\\directory\\file.txt'

    path = file_system.JoinPath([
        u'\\\\server\\share', u'directory', u'file.txt'])
    self.assertEqual(path, expected_path)

    platform.system = original_platform_system


if __name__ == '__main__':
  unittest.main()
