#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the encoded stream file entry implementation."""

import os
import unittest

from dfvfs.lib import definitions
from dfvfs.path import encoded_stream_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import encoded_stream_file_entry
from dfvfs.vfs import encoded_stream_file_system


class EncodedStreamFileEntryTest(unittest.TestCase):
  """The unit test for the encoded stream file entry object."""

  _RC4_KEY = b'rc4test'

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'syslog.base64')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._encoded_stream_path_spec = (
        encoded_stream_path_spec.EncodedStreamPathSpec(
            encoding_method=definitions.ENCODING_METHOD_BASE64,
            parent=path_spec))

    self._file_system = (
        encoded_stream_file_system.EncodedStreamFileSystem(
            self._resolver_context))
    self._file_system.Open(self._encoded_stream_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()

  def testInitialize(self):
    """Test the initialize functionality."""
    file_entry = encoded_stream_file_entry.EncodedStreamFileEntry(
        self._resolver_context, self._file_system,
        self._encoded_stream_path_spec)
    self.assertIsNotNone(file_entry)

  def testGetFileEntryByPathSpec(self):
    """Test the get a file entry by path specification functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._encoded_stream_path_spec)
    self.assertIsNotNone(file_entry)

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._encoded_stream_path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertIsNone(parent_file_entry)

  def testGetStat(self):
    """Tests the GetStat function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._encoded_stream_path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry.GetStat()
    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 1247)

  def testIsFunctions(self):
    """Test the Is? functions."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._encoded_stream_path_spec)
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
        self._encoded_stream_path_spec)
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
