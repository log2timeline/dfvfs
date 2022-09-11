#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the data range file entry implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import data_range_file_entry
from dfvfs.vfs import data_range_file_system

from tests import test_lib as shared_test_lib


class DataRangeFileEntryTest(shared_test_lib.BaseTestCase):
  """Tests the data range file entry."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['syslog'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._data_range_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_DATA_RANGE, parent=test_os_path_spec,
        range_offset=0x1c0, range_size=0x41)

    self._file_system = data_range_file_system.DataRangeFileSystem(
        self._resolver_context, self._data_range_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Test the __init__ function."""
    file_entry = data_range_file_entry.DataRangeFileEntry(
        self._resolver_context, self._file_system,
        self._data_range_path_spec)
    self.assertIsNotNone(file_entry)

  def testSize(self):
    """Test the size property."""
    file_entry = data_range_file_entry.DataRangeFileEntry(
        self._resolver_context, self._file_system,
        self._data_range_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 0x41)

  def testGetFileEntryByPathSpec(self):
    """Test the get a file entry by path specification functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._data_range_path_spec)
    self.assertIsNotNone(file_entry)

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._data_range_path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertIsNone(parent_file_entry)

  def testIsFunctions(self):
    """Test the Is? functions."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._data_range_path_spec)
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
        self._data_range_path_spec)
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
        self._data_range_path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._data_range_path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = ''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, data_stream_name)

    data_stream = file_entry.GetDataStream('bogus')
    self.assertIsNone(data_stream)


if __name__ == '__main__':
  unittest.main()
