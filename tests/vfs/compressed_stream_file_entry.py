#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the compressed stream file entry implementation."""

import os
import unittest

from dfvfs.lib import definitions
from dfvfs.path import compressed_stream_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import compressed_stream_file_entry
from dfvfs.vfs import compressed_stream_file_system


class CompressedStreamFileEntryTest(unittest.TestCase):
  """The unit test for the compressed stream file entry object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'syslog.bz2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._compressed_stream_path_spec = (
        compressed_stream_path_spec.CompressedStreamPathSpec(
            compression_method=definitions.COMPRESSION_METHOD_BZIP2,
            parent=path_spec))

    self._file_system = (
        compressed_stream_file_system.CompressedStreamFileSystem(
            self._resolver_context))
    self._file_system.Open(path_spec=self._compressed_stream_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()

  def testIntialize(self):
    """Test the initialize functionality."""
    file_entry = compressed_stream_file_entry.CompressedStreamFileEntry(
        self._resolver_context, self._file_system,
        self._compressed_stream_path_spec)
    self.assertNotEqual(file_entry, None)

  def testGetFileEntryByPathSpec(self):
    """Test the get a file entry by path specification functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._compressed_stream_path_spec)
    self.assertNotEqual(file_entry, None)

  def testGetParentFileEntry(self):
    """Test the get parent file entry functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._compressed_stream_path_spec)
    self.assertNotEqual(file_entry, None)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertEqual(parent_file_entry, None)

  def testGetStat(self):
    """Test the get stat functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._compressed_stream_path_spec)
    self.assertNotEqual(file_entry, None)

    stat_object = file_entry.GetStat()
    self.assertNotEqual(stat_object, None)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)

  def testIsFunctions(self):
    """Test the Is? functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._compressed_stream_path_spec)
    self.assertNotEqual(file_entry, None)

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
        self._compressed_stream_path_spec)
    self.assertNotEqual(file_entry, None)

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
