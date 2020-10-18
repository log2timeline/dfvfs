#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the partition file entry implementation using pytsk3."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import tsk_partition_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import tsk_partition_file_entry
from dfvfs.vfs import tsk_partition_file_system

from tests import test_lib as shared_test_lib


class TSKPartitionDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the TSK partition directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['mbr.raw'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._tsk_partition_path_spec = (
        tsk_partition_path_spec.TSKPartitionPathSpec(
            location='/', parent=self._os_path_spec))

    self._file_system = tsk_partition_file_system.TSKPartitionFileSystem(
        self._resolver_context)
    self._file_system.Open(self._tsk_partition_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = tsk_partition_file_entry.TSKPartitionDirectory(
        self._file_system, self._tsk_partition_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = tsk_partition_file_entry.TSKPartitionDirectory(
        self._file_system, self._tsk_partition_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 8)


class TSKPartitionFileEntryTest(shared_test_lib.BaseTestCase):
  """TSK partition file entry tests."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['mbr.raw'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._tsk_partition_path_spec = (
        tsk_partition_path_spec.TSKPartitionPathSpec(
            location='/', parent=self._os_path_spec))

    self._file_system = tsk_partition_file_system.TSKPartitionFileSystem(
        self._resolver_context)
    self._file_system.Open(self._tsk_partition_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  # mmls test_data/mbr.raw
  # DOS Partition Table
  # Offset Sector: 0
  # Units are in 512-byte sectors
  #
  #       Slot      Start        End          Length       Description
  # 000:  Meta      0000000000   0000000000   0000000001   Primary Table (#0)
  # 001:  -------   0000000000   0000000000   0000000001   Unallocated
  # 002:  000:000   0000000001   0000000129   0000000129   Linux (0x83)
  # 003:  Meta      0000000130   0000008191   0000008062   DOS Extended (0x05)
  # 004:  Meta      0000000130   0000000130   0000000001   Extended Table (#1)
  # 005:  -------   0000000130   0000000130   0000000001   Unallocated
  # 006:  001:000   0000000131   0000000259   0000000129   Linux (0x83)
  # 007:  -------   0000000260   0000008191   0000007932   Unallocated

  def testIntialize(self):
    """Test the __init__ function."""
    file_entry = tsk_partition_file_entry.TSKPartitionFileEntry(
        self._resolver_context, self._file_system,
        self._tsk_partition_path_spec, is_virtual=True)

    self.assertIsNotNone(file_entry)

  # TODO: add tests for _GetDirectory
  # TODO: add tests for _GetSubFileEntries

  def testName(self):
    """Test the name property."""
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=2, parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'p1')

  def testSize(self):
    """Test the size property."""
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=2, parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 66048)

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=1, parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertIsNone(parent_file_entry)

  def testGetStat(self):
    """Tests the GetStat function."""
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=1, parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry.GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 512)

  # TODO: add tests for GetTSKVsPart

  def testIsFunctions(self):
    """Test the Is? functions."""
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=1, parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertFalse(file_entry.IsRoot())
    self.assertFalse(file_entry.IsVirtual())
    self.assertFalse(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertFalse(file_entry.IsDirectory())
    self.assertTrue(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertTrue(file_entry.IsRoot())
    self.assertTrue(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertTrue(file_entry.IsDirectory())
    self.assertFalse(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

  def testSubFileEntries(self):
    """Test the sub file entries iteration functionality."""
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 8)

    expected_sub_file_entry_names = ['', '', '', '', '', '', 'p1', 'p2']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))

  def testDataStreams(self):
    """Test the data streams functionality."""
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=1, parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=1, parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = ''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, data_stream_name)

    data_stream = file_entry.GetDataStream('bogus')
    self.assertIsNone(data_stream)


if __name__ == '__main__':
  unittest.main()
