#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the compressed stream file entry implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.lib import definitions
from dfvfs.path import compressed_stream_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import compressed_stream_file_entry
from dfvfs.vfs import compressed_stream_file_system

from tests import test_lib as shared_test_lib


class CompressedStreamFileEntryTest(shared_test_lib.BaseTestCase):
  """Tests the compressed stream file entry."""

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

    self._file_system = (
        compressed_stream_file_system.CompressedStreamFileSystem(
            self._resolver_context))
    self._file_system.Open(self._compressed_stream_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testInitialize(self):
    """Test the __init__ function."""
    file_entry = compressed_stream_file_entry.CompressedStreamFileEntry(
        self._resolver_context, self._file_system,
        self._compressed_stream_path_spec)
    self.assertIsNotNone(file_entry)

  def testSize(self):
    """Test the size property."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._compressed_stream_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 1247)

  def testGetFileEntryByPathSpec(self):
    """Test the get a file entry by path specification functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._compressed_stream_path_spec)
    self.assertIsNotNone(file_entry)

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._compressed_stream_path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertIsNone(parent_file_entry)

  def testGetStat(self):
    """Tests the GetStat function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._compressed_stream_path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry.GetStat()
    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 1247)

  def testIsFunctions(self):
    """Test the Is? functions."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._compressed_stream_path_spec)
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
        self._compressed_stream_path_spec)
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

  def testDataStreams(self):
    """Test the data streams functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._compressed_stream_path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._compressed_stream_path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = ''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, data_stream_name)

    data_stream = file_entry.GetDataStream('bogus')
    self.assertIsNone(data_stream)


if __name__ == '__main__':
  unittest.main()
