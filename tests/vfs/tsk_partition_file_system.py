#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for a partition file system implementation using pytsk3."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import tsk_partition_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import tsk_partition_file_system

from tests import test_lib as shared_test_lib


class TSKPartitionFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests the TSK partition file system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['mbr.raw'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._tsk_partition_path_spec = (
        tsk_partition_path_spec.TSKPartitionPathSpec(
            location='/', parent=self._os_path_spec))

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  # mmls test_data/mbr.raw
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
        location='/', parent=self._os_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=3, parent=self._os_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=6, parent=self._os_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p2', parent=self._os_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=9, parent=self._os_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p0', parent=self._os_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p9', parent=self._os_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = tsk_partition_file_system.TSKPartitionFileSystem(
        self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._tsk_partition_path_spec)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=3, parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=6, parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'p2')

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p2', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'p2')

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=9, parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p0', parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p9', parent=self._os_path_spec)
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
    self.assertEqual(file_entry.name, '')

    file_system.Close()


if __name__ == '__main__':
  unittest.main()
