#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the directory implementation using the CPIOArchiveFile."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import cpio_directory
from dfvfs.vfs import cpio_file_system

from tests import test_lib as shared_test_lib


class CPIODirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the CPIO directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['syslog.bin.cpio'])
    self._SkipIfPathNotExists(test_path)

    self._os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._cpio_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CPIO, location='/syslog',
        parent=self._os_path_spec)

    self._file_system = cpio_file_system.CPIOFileSystem(
        self._resolver_context, self._cpio_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = cpio_directory.CPIODirectory(
        self._file_system, self._cpio_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = cpio_directory.CPIODirectory(
        self._file_system, self._cpio_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 1)


if __name__ == '__main__':
  unittest.main()
