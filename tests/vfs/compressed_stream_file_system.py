#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the compressed stream file system implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.lib import definitions
from dfvfs.path import compressed_stream_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import compressed_stream_file_system

from tests import test_lib as shared_test_lib


class CompressedStreamFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests the compressed stream file system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.bz2'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._compressed_stream_path_spec = (
        compressed_stream_path_spec.CompressedStreamPathSpec(
            compression_method=definitions.COMPRESSION_METHOD_BZIP2,
            parent=path_spec))

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = compressed_stream_file_system.CompressedStreamFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._compressed_stream_path_spec)

    file_system.Close()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = compressed_stream_file_system.CompressedStreamFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._compressed_stream_path_spec)

    self.assertTrue(file_system.FileEntryExistsByPathSpec(
        self._compressed_stream_path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = compressed_stream_file_system.CompressedStreamFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._compressed_stream_path_spec)

    file_entry = file_system.GetFileEntryByPathSpec(
        self._compressed_stream_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    file_system.Close()

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = compressed_stream_file_system.CompressedStreamFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._compressed_stream_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    file_system.Close()


if __name__ == '__main__':
  unittest.main()
