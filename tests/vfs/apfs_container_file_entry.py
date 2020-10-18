#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the APFS container file entry implementation using pyfsapfs."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import apfs_container_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import raw_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import apfs_container_file_entry
from dfvfs.vfs import apfs_container_file_system

from tests import test_lib as shared_test_lib


class APFSContainerDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the APFS container directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['apfs.raw'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._raw_path_spec = raw_path_spec.RawPathSpec(parent=path_spec)
    self._apfs_container_path_spec = (
        apfs_container_path_spec.APFSContainerPathSpec(
            location='/', parent=self._raw_path_spec))

    self._file_system = apfs_container_file_system.APFSContainerFileSystem(
        self._resolver_context)
    self._file_system.Open(self._apfs_container_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = apfs_container_file_entry.APFSContainerDirectory(
        self._file_system, self._apfs_container_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = apfs_container_file_entry.APFSContainerDirectory(
        self._file_system, self._apfs_container_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 1)


class APFSContainerFileEntryTest(shared_test_lib.BaseTestCase):
  """APFS container file entry tests."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['apfs.raw'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._raw_path_spec = raw_path_spec.RawPathSpec(parent=path_spec)
    self._apfs_container_path_spec = (
        apfs_container_path_spec.APFSContainerPathSpec(
            location='/', parent=self._raw_path_spec))

    self._file_system = apfs_container_file_system.APFSContainerFileSystem(
        self._resolver_context)
    self._file_system.Open(self._apfs_container_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testInitialize(self):
    """Test the __init__ function."""
    file_entry = apfs_container_file_entry.APFSContainerFileEntry(
        self._resolver_context, self._file_system,
        self._apfs_container_path_spec, is_virtual=True)

    self.assertIsNotNone(file_entry)

  # TODO: test _GetDirectory
  # TODO: test _GetSubFileEntries

  def testName(self):
    """Test the name property."""
    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        parent=self._raw_path_spec, volume_index=0)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'apfs1')

  def testSize(self):
    """Test the size property."""
    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        parent=self._raw_path_spec, volume_index=0)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 0)

  def testGetAPFSVolume(self):
    """Test the GetAPFSVolume function."""
    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        parent=self._raw_path_spec, volume_index=0)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    fsapfs_volume = file_entry.GetAPFSVolume()
    self.assertIsNotNone(fsapfs_volume)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    fsapfs_volume = file_entry.GetAPFSVolume()
    self.assertIsNone(fsapfs_volume)

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        parent=self._raw_path_spec, volume_index=0)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertIsNotNone(parent_file_entry)

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertIsNone(parent_file_entry)

  def testGetStat(self):
    """Tests the GetStat function."""
    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        parent=self._raw_path_spec, volume_index=0)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry.GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)

  def testIsFunctions(self):
    """Test the Is? functions."""
    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        parent=self._raw_path_spec, volume_index=0)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertFalse(file_entry.IsRoot())
    self.assertFalse(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertFalse(file_entry.IsDirectory())
    self.assertTrue(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/', parent=self._raw_path_spec)
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
    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 1)

    expected_sub_file_entry_names = ['apfs1']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))

  def testDataStreams(self):
    """Test the data streams functionality."""
    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        parent=self._raw_path_spec, volume_index=0)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        parent=self._raw_path_spec, volume_index=0)
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
