#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the fake file system implementation."""

import unittest

from dfvfs.path import fake_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import fake_file_system


class FakeFileSystemTest(unittest.TestCase):
  """The unit test for the fake file system object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def testIntialize(self):
    """Test the intialize functionality."""
    file_system = fake_file_system.FakeFileSystem(self._resolver_context)

    self.assertNotEquals(file_system, None)

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = fake_file_system.FakeFileSystem(self._resolver_context)
    file_system.AddFileEntry(
        u'/test_data/testdir_fake/file1.txt', file_data='FILE1')

    path_spec = fake_path_spec.FakePathSpec(
        location=u'/test_data/testdir_fake/file1.txt')
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = fake_path_spec.FakePathSpec(
        location=u'/test_data/testdir_fake/file6.txt')
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

  def testGetFileEntryByPathSpec(self):
    """Test the get entry by path specification functionality."""
    file_system = fake_file_system.FakeFileSystem(self._resolver_context)
    file_system.AddFileEntry(
        u'/test_data/testdir_fake/file1.txt', file_data='FILE1')

    path_spec = fake_path_spec.FakePathSpec(
        location=u'/test_data/testdir_fake/file1.txt')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)
    self.assertEquals(file_entry.name, u'file1.txt')

    path_spec = fake_path_spec.FakePathSpec(
        location=u'/test_data/testdir_fake/file6.txt')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertEquals(file_entry, None)

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = fake_file_system.FakeFileSystem(self._resolver_context)

    file_entry = file_system.GetRootFileEntry()

    self.assertNotEquals(file_entry, None)
    self.assertEquals(file_entry.name, u'')


if __name__ == '__main__':
  unittest.main()
