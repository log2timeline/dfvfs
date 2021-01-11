#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the operating system file system implementation."""

import os
import platform
import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import os_file_system

from tests import test_lib as shared_test_lib


def TestPlatformSystem():
  """Test function to emulate platform.system() == 'Windows'"""
  return 'Windows'


class OSFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests the operating system file system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testIntialize(self):
    """Test the __init__ function."""
    test_path = self._GetTestFilePath(['testdir_os'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    file_system = os_file_system.OSFileSystem(
        self._resolver_context, test_os_path_spec)

    self.assertIsNotNone(file_system)

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    test_path = self._GetTestFilePath(['testdir_os'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    file_system = os_file_system.OSFileSystem(
        self._resolver_context, test_os_path_spec)

    test_path = self._GetTestFilePath(['testdir_os', 'file1.txt'])
    self._SkipIfPathNotExists(test_path)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    test_path = self._GetTestFilePath(['testdir_os', 'file6.txt'])
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    test_path = self._GetTestFilePath(['testdir_os'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    file_system = os_file_system.OSFileSystem(
        self._resolver_context, test_os_path_spec)

    test_path = self._GetTestFilePath(['testdir_os', 'file1.txt'])
    self._SkipIfPathNotExists(test_path)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'file1.txt')

    test_path = self._GetTestFilePath(['testdir_os', 'file6.txt'])
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    test_path = self._GetTestFilePath(['testdir_os'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    file_system = os_file_system.OSFileSystem(
        self._resolver_context, test_os_path_spec)

    if platform.system() == 'Windows':
      # Return the root with the drive letter of the volume the current
      # working directory is on.
      expected_location = os.getcwd()
      expected_location, _, _ = expected_location.partition('\\')
    else:
      expected_location = ''

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, expected_location)

  def testJoinPathWindows(self):
    """Test the join path functionality for Windows."""
    # In this test we emulate we are running on Windows.
    original_platform_system = platform.system
    platform.system = TestPlatformSystem

    test_path = self._GetTestFilePath(['testdir_os'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    file_system = os_file_system.OSFileSystem(
        self._resolver_context, test_os_path_spec)
    file_system.PATH_SEPARATOR = '\\'

    expected_path = '\\\\.\\PhysicalDrive0'

    path = file_system.JoinPath(['\\\\.\\PhysicalDrive0'])
    self.assertEqual(path, expected_path)

    expected_path = '\\\\.\\C:'

    path = file_system.JoinPath(['\\\\.\\C:'])
    self.assertEqual(path, expected_path)

    expected_path = 'C:'

    path = file_system.JoinPath(['\\\\.\\C:\\'])
    self.assertEqual(path, expected_path)

    expected_path = (
        '\\\\?\\Volume{26a21bda-a627-11d7-9931-806e6f6e6963}\\test1')

    path = file_system.JoinPath([
        '\\\\?\\Volume{26a21bda-a627-11d7-9931-806e6f6e6963}\\', 'test1'])
    self.assertEqual(path, expected_path)

    expected_path = 'C:\\test1\\test2\\test3'

    path = file_system.JoinPath(['C:', 'test1', 'test2', 'test3'])
    self.assertEqual(path, expected_path)

    path = file_system.JoinPath([
        'C:\\', 'test1\\\\', '\\\\test2', 'test3\\'])
    self.assertEqual(path, expected_path)

    path = file_system.JoinPath(['C:\\test1\\\\', '\\\\test2\\test3'])
    self.assertEqual(path, expected_path)

    path = file_system.JoinPath(['\\\\.\\C:\\', 'test1', 'test2', 'test3'])
    self.assertEqual(path, expected_path)

    expected_path = '\\\\server\\share\\directory\\file.txt'

    path = file_system.JoinPath([
        '\\\\server\\share', 'directory', 'file.txt'])
    self.assertEqual(path, expected_path)

    platform.system = original_platform_system


if __name__ == '__main__':
  unittest.main()
