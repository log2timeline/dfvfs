#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the directory implementation using pyvshadow."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import vshadow_directory
from dfvfs.vfs import vshadow_file_system

from tests import test_lib as shared_test_lib


class VShadowDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the Volume Shadow Snapshot (VSS) directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['vss.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._vshadow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, location='/',
        parent=self._raw_path_spec)

    self._file_system = vshadow_file_system.VShadowFileSystem(
        self._resolver_context, self._vshadow_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = vshadow_directory.VShadowDirectory(
        self._file_system, self._vshadow_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = vshadow_directory.VShadowDirectory(
        self._file_system, self._vshadow_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 2)


if __name__ == '__main__':
  unittest.main()
