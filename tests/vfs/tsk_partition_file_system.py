#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for a partition file system implementation using pytsk3."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import tsk_partition_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import tsk_partition_file_system


class TSKPartitionFileSystemTest(unittest.TestCase):
  """The unit test for the TSK partition file system object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'tsk_volume_system.raw')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._tsk_partition_path_spec = (
        tsk_partition_path_spec.TSKPartitionPathSpec(
            location=u'/', parent=self._os_path_spec))

  # mmls test_data/tsk_volume_system.raw
  # DOS Partition Table
  # Offset Sector: 0
  # Units are in 512-byte sectors
  #
  #      Slot    Start        End          Length       Description
  # 00:  Meta    0000000000   0000000000   0000000001   Primary Table (#0)
  # 01:  -----   0000000000   0000000000   0000000001   Unallocated
  # 02:  00:00   0000000001   0000000350   0000000350   Linux (0x83)
  # 03:  Meta    0000000351   0000002879   0000002529   DOS Extended (0x05)
  # 04:  Meta    0000000351   0000000351   0000000001   Extended Table (#1)
  # 05:  -----   0000000351   0000000351   0000000001   Unallocated
  # 06:  01:00   0000000352   0000002879   0000002528   Linux (0x83)

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = tsk_partition_file_system.TSKPartitionFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._tsk_partition_path_spec)

    file_system.Close()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = tsk_partition_file_system.TSKPartitionFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._tsk_partition_path_spec)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=u'/', parent=self._os_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=3, parent=self._os_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=6, parent=self._os_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=u'/p2', parent=self._os_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=9, parent=self._os_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=u'/p0', parent=self._os_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=u'/p9', parent=self._os_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = tsk_partition_file_system.TSKPartitionFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._tsk_partition_path_spec)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=u'/', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, u'')

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=3, parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, u'')

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=6, parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, u'p2')

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=u'/p2', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, u'p2')

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=9, parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=u'/p0', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=u'/p9', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    file_system.Close()

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = tsk_partition_file_system.TSKPartitionFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._tsk_partition_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, u'')

    file_system.Close()


if __name__ == '__main__':
  unittest.main()
