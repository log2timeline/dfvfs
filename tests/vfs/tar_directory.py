#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the directory implementation using the tarfile."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import tar_directory
from dfvfs.vfs import tar_file_system

from tests import test_lib as shared_test_lib


class TARDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the TAR extracted directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['syslog.tar'])
    self._SkipIfPathNotExists(test_path)

    self._os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._tar_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TAR, location='/',
        parent=self._os_path_spec)

    self._file_system = tar_file_system.TARFileSystem(
        self._resolver_context, self._tar_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = tar_directory.TARDirectory(
        self._file_system, self._tar_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = tar_directory.TARDirectory(
        self._file_system, self._tar_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 1)


if __name__ == '__main__':
  unittest.main()
