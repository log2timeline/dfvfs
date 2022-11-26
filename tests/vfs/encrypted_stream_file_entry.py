#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the encrypted stream file entry implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.resolver import resolver
from dfvfs.vfs import encrypted_stream_file_entry
from dfvfs.vfs import encrypted_stream_file_system

from tests import test_lib as shared_test_lib


class EncryptedStreamFileEntryTest(shared_test_lib.BaseTestCase):
  """Tests for the encrypted stream file entry."""

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

    self._file_system = encrypted_stream_file_system.EncryptedStreamFileSystem(
        self._resolver_context, self._encrypted_stream_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Test the __init__ function."""
    file_entry = encrypted_stream_file_entry.EncryptedStreamFileEntry(
        self._resolver_context, self._file_system,
        self._encrypted_stream_path_spec)
    self.assertIsNotNone(file_entry)

  def testSize(self):
    """Test the size property."""
    file_entry = encrypted_stream_file_entry.EncryptedStreamFileEntry(
        self._resolver_context, self._file_system,
        self._encrypted_stream_path_spec)

    self.assertIsNotNone(file_entry)

    try:
      self.assertEqual(file_entry.size, 1247)
    except errors.BackEndError:
      raise unittest.SkipTest('missing cryptograpy support')

  def testGetFileEntryByPathSpec(self):
    """Test the get a file entry by path specification functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._encrypted_stream_path_spec)
    self.assertIsNotNone(file_entry)

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._encrypted_stream_path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertIsNone(parent_file_entry)

  def testIsFunctions(self):
    """Test the Is? functions."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._encrypted_stream_path_spec)
    self.assertIsNotNone(file_entry)

    self.assertTrue(file_entry.IsRoot())
    self.assertTrue(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertFalse(file_entry.IsDirectory())
    self.assertTrue(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

  def testSubFileEntries(self):
    """Test the sub file entries iteration functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._encrypted_stream_path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 0)

    expected_sub_file_entry_names = []

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), expected_sub_file_entry_names)


if __name__ == '__main__':
  unittest.main()
