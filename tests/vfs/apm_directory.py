#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the directory implementation using pyvsapm."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import apm_directory
from dfvfs.vfs import apm_file_system

from tests import test_lib as shared_test_lib


class APMDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the APM directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['apm.dmg'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._modi_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_MODI, parent=test_os_path_spec)
    self._apm_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APM, location='/',
        parent=self._modi_path_spec)

    self._file_system = apm_file_system.APMFileSystem(
        self._resolver_context, self._apm_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = apm_directory.APMDirectory(
        self._file_system, self._apm_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = apm_directory.APMDirectory(
        self._file_system, self._apm_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 2)


if __name__ == '__main__':
  unittest.main()
