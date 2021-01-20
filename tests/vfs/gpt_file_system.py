#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for a file system implementation using pyvsgpt."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import gpt_file_system

from tests import test_lib as shared_test_lib


class GPTFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests the GPT file system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['gpt.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._gpt_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GPT, location='/',
        parent=self._raw_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  # vsgptinfo gpt.raw
  #
  # GUID Partition Table (GPT) information:
  #   Disk identifier      : 25271092-82a1-4e85-9be8-2eb59926af3f
  #   Bytes per sector     : 512
  #   Number of partitions : 2
  #
  # Partition: 1
  #   Identifier           : b6d37ab4-051f-4556-97d2-ad1f8a609644
  #   Type identifier      : 0fc63daf-8483-4772-8e79-3d69d8477de4
  #   Type                 : 0x00 (Empty)
  #   Offset               : 1048576 (0x00100000)
  #   Size                 : 65024
  #
  # Partition: 2
  #   Identifier           : a03faa35-d9a1-4315-a644-681506850073
  #   Type identifier      : 0fc63daf-8483-4772-8e79-3d69d8477de4
  #   Type                 : 0x00 (Empty)
  #   Offset               : 2097152 (0x00200000)
  #   Size                 : 65024

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = gpt_file_system.GPTFileSystem(
        self._resolver_context, self._gpt_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

  def testFileEntryExistsByPathSpec(self):
    """Tests the FileEntryExistsByPathSpec function."""
    file_system = gpt_file_system.GPTFileSystem(
        self._resolver_context, self._gpt_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GPT, location='/',
        parent=self._raw_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GPT, entry_index=0,
        parent=self._raw_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GPT, location='/p1',
        parent=self._raw_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GPT, entry_index=9,
        parent=self._raw_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GPT, location='/p0',
        parent=self._raw_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GPT, location='/p9',
        parent=self._raw_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = gpt_file_system.GPTFileSystem(
        self._resolver_context, self._gpt_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GPT, location='/',
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GPT, entry_index=0,
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'p1')

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GPT, location='/p1',
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'p1')

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GPT, entry_index=9,
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GPT, location='/p0',
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GPT, location='/p9',
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = gpt_file_system.GPTFileSystem(
        self._resolver_context, self._gpt_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')


if __name__ == '__main__':
  unittest.main()
