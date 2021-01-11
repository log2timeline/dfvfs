#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the encrypted stream file system implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.resolver import resolver
from dfvfs.vfs import encrypted_stream_file_system

from tests import test_lib as shared_test_lib


class EncryptedStreamFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests the compressed stream file system."""

  _RC4_KEY = b'rc4test'

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['syslog.rc4'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._encrypted_stream_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ENCRYPTED_STREAM,
        encryption_method=definitions.ENCRYPTION_METHOD_RC4,
        parent=test_os_path_spec)
    resolver.Resolver.key_chain.SetCredential(
        self._encrypted_stream_path_spec, 'key', self._RC4_KEY)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = encrypted_stream_file_system.EncryptedStreamFileSystem(
        self._resolver_context, self._encrypted_stream_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = encrypted_stream_file_system.EncryptedStreamFileSystem(
        self._resolver_context, self._encrypted_stream_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    self.assertTrue(file_system.FileEntryExistsByPathSpec(
        self._encrypted_stream_path_spec))

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = encrypted_stream_file_system.EncryptedStreamFileSystem(
        self._resolver_context, self._encrypted_stream_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    file_entry = file_system.GetFileEntryByPathSpec(
        self._encrypted_stream_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = encrypted_stream_file_system.EncryptedStreamFileSystem(
        self._resolver_context, self._encrypted_stream_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')


if __name__ == '__main__':
  unittest.main()
