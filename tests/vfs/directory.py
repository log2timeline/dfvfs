#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the VFS directory interface."""

import unittest

from dfvfs.path import fake_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import directory
from dfvfs.vfs import fake_file_system

from tests import test_lib as shared_test_lib


class DirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the VFS directory interface."""

  # pylint: disable=protected-access

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    self._path_spec = fake_path_spec.FakePathSpec(location='/')

    self._file_system = fake_file_system.FakeFileSystem(
        self._resolver_context, self._path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    test_directory = directory.Directory(self._file_system, self._path_spec)

    generator = test_directory._EntriesGenerator()
    self.assertIsNotNone(generator)

  def testEntries(self):
    """Tests the entries property."""
    test_directory = directory.Directory(self._file_system, self._path_spec)

    self.assertEqual(list(test_directory.entries), [])


if __name__ == '__main__':
  unittest.main()
