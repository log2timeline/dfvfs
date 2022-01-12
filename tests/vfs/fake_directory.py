#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the fake directory implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import fake_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import fake_directory
from dfvfs.vfs import fake_file_system

from tests import test_lib as shared_test_lib


class FakeDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the fake directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    self._fake_path_spec = fake_path_spec.FakePathSpec(location='/')

    self._file_system = fake_file_system.FakeFileSystem(
        self._resolver_context, self._fake_path_spec)

    self._file_system.AddFileEntry(
        '/test_data/testdir_fake',
        file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)
    self._file_system.AddFileEntry(
        '/test_data/testdir_fake/file1.txt', file_data=b'FILE1')
    self._file_system.AddFileEntry(
        '/test_data/testdir_fake/file2.txt', file_data=b'FILE2')
    self._file_system.AddFileEntry(
        '/test_data/testdir_fake/file3.txt', file_data=b'FILE3')
    self._file_system.AddFileEntry(
        '/test_data/testdir_fake/file4.txt', file_data=b'FILE4')
    self._file_system.AddFileEntry(
        '/test_data/testdir_fake/file5.txt', file_data=b'FILE5')

    self._file_system.AddFileEntry(
        '/test_data/testdir_fake/link1.txt',
        file_entry_type=definitions.FILE_ENTRY_TYPE_LINK,
        link_data='/test_data/testdir_fake/file1.txt')

    self._test_file = '/test_data/testdir_fake'

    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = fake_directory.FakeDirectory(
        self._file_system, self._fake_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = fake_directory.FakeDirectory(
        self._file_system, self._fake_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 0)


if __name__ == '__main__':
  unittest.main()
