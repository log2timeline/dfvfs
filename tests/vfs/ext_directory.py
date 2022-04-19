#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the directory implementation using pyfsext."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import ext_directory
from dfvfs.vfs import ext_file_system

from tests import test_lib as shared_test_lib


class EXTDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the EXT directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['ext2.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, location='/',
        parent=self._raw_path_spec)

    self._file_system = ext_file_system.EXTFileSystem(
        self._resolver_context, self._ext_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    fsext_file_entry = self._file_system.GetEXTFileEntryByPathSpec(
        self._ext_path_spec)

    directory = ext_directory.EXTDirectory(
        self._file_system, self._ext_path_spec, fsext_file_entry)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    fsext_file_entry = self._file_system.GetEXTFileEntryByPathSpec(
        self._ext_path_spec)

    directory = ext_directory.EXTDirectory(
        self._file_system, self._ext_path_spec, fsext_file_entry)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 4)


if __name__ == '__main__':
  unittest.main()
