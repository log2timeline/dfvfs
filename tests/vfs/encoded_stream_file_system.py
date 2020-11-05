#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the encoded stream file system implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.lib import definitions
from dfvfs.path import encoded_stream_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import encoded_stream_file_system

from tests import test_lib as shared_test_lib


class EncodedStreamFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests the compressed stream file system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.base64'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._encoded_stream_path_spec = (
        encoded_stream_path_spec.EncodedStreamPathSpec(
            encoding_method=definitions.ENCODING_METHOD_BASE64,
            parent=path_spec))

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = encoded_stream_file_system.EncodedStreamFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._encoded_stream_path_spec)

    file_system.Close()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = encoded_stream_file_system.EncodedStreamFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._encoded_stream_path_spec)

    self.assertTrue(file_system.FileEntryExistsByPathSpec(
        self._encoded_stream_path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = encoded_stream_file_system.EncodedStreamFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._encoded_stream_path_spec)

    file_entry = file_system.GetFileEntryByPathSpec(
        self._encoded_stream_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    file_system.Close()

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = encoded_stream_file_system.EncodedStreamFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._encoded_stream_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    file_system.Close()


if __name__ == '__main__':
  unittest.main()
