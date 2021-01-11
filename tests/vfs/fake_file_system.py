#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the fake file system implementation."""

import unittest

from dfvfs.path import fake_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import fake_file_system

from tests import test_lib as shared_test_lib


class FakeFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests for the fake file system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    self._fake_path_spec = fake_path_spec.FakePathSpec(location='/')

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = fake_file_system.FakeFileSystem(
        self._resolver_context, self._fake_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = fake_file_system.FakeFileSystem(
        self._resolver_context, self._fake_path_spec)
    self.assertIsNotNone(file_system)

    file_system.AddFileEntry(
        '/test_data/testdir_fake/file1.txt', file_data=b'FILE1')

    file_system.Open()

    path_spec = fake_path_spec.FakePathSpec(
        location='/test_data/testdir_fake/file1.txt')
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = fake_path_spec.FakePathSpec(
        location='/test_data/testdir_fake/file6.txt')
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = fake_file_system.FakeFileSystem(
        self._resolver_context, self._fake_path_spec)
    self.assertIsNotNone(file_system)

    file_system.AddFileEntry(
        '/test_data/testdir_fake/file1.txt', file_data=b'FILE1')

    file_system.Open()

    path_spec = fake_path_spec.FakePathSpec(
        location='/test_data/testdir_fake/file1.txt')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'file1.txt')

    path_spec = fake_path_spec.FakePathSpec(
        location='/test_data/testdir_fake/file6.txt')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = fake_file_system.FakeFileSystem(
        self._resolver_context, self._fake_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')


if __name__ == '__main__':
  unittest.main()
