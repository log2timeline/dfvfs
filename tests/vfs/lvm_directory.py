#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the directory implementation using pyvslvm."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import lvm_directory
from dfvfs.vfs import lvm_file_system

from tests import test_lib as shared_test_lib


class LVMDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the LVM directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['lvm.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._lvm_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_LVM, location='/',
        parent=self._raw_path_spec)

    self._file_system = lvm_file_system.LVMFileSystem(
        self._resolver_context, self._lvm_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = lvm_directory.LVMDirectory(
        self._file_system, self._lvm_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = lvm_directory.LVMDirectory(
        self._file_system, self._lvm_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 2)


if __name__ == '__main__':
  unittest.main()
