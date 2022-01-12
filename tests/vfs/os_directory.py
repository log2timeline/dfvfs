#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the operating system directory implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import os_directory
from dfvfs.vfs import os_file_system

from tests import test_lib as shared_test_lib


class OSDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the operating system directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['testdir_os'])
    self._SkipIfPathNotExists(test_path)

    self._os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    self._file_system = os_file_system.OSFileSystem(
        self._resolver_context, self._os_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = os_directory.OSDirectory(
        self._file_system, self._os_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = os_directory.OSDirectory(
        self._file_system, self._os_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 6)


if __name__ == '__main__':
  unittest.main()
