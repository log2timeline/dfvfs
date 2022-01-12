#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the APFS container directory implementation using pyfsapfs."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import apfs_container_directory
from dfvfs.vfs import apfs_container_file_system

from tests import test_lib as shared_test_lib


class APFSContainerDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the APFS container directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['apfs.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._apfs_container_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, location='/',
        parent=self._raw_path_spec)

    self._file_system = apfs_container_file_system.APFSContainerFileSystem(
        self._resolver_context, self._apfs_container_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = apfs_container_directory.APFSContainerDirectory(
        self._file_system, self._apfs_container_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = apfs_container_directory.APFSContainerDirectory(
        self._file_system, self._apfs_container_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 1)


if __name__ == '__main__':
  unittest.main()
