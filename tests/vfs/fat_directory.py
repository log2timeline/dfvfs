#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the directory implementation using pyfsfat."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import fat_directory
from dfvfs.vfs import fat_file_system

from tests import test_lib as shared_test_lib


class FATDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the FAT directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['fat12.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._fat_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_FAT, location='\\',
        parent=self._raw_path_spec)

    self._file_system = fat_file_system.FATFileSystem(
        self._resolver_context, self._fat_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    fsfat_file_entry = self._file_system.GetFATFileEntryByPathSpec(
        self._fat_path_spec)

    directory = fat_directory.FATDirectory(
        self._file_system, self._fat_path_spec, fsfat_file_entry)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    fsfat_file_entry = self._file_system.GetFATFileEntryByPathSpec(
        self._fat_path_spec)

    directory = fat_directory.FATDirectory(
        self._file_system, self._fat_path_spec, fsfat_file_entry)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 2)


if __name__ == '__main__':
  unittest.main()
