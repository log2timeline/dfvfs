#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the operating system file entry implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import os_file_entry
from dfvfs.vfs import os_file_system

from tests import test_lib as shared_test_lib


class OSDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the operating system directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['testdir_os'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)

    self._file_system = os_file_system.OSFileSystem(self._resolver_context)
    self._file_system.Open(self._os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = os_file_entry.OSDirectory(
        self._file_system, self._os_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = os_file_entry.OSDirectory(
        self._file_system, self._os_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 6)


class OSFileEntryTest(shared_test_lib.BaseTestCase):
  """Tests the operating system file entry."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['testdir_os'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)

    self._file_system = os_file_system.OSFileSystem(self._resolver_context)
    self._file_system.Open(self._os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testIntialize(self):
    """Test the __init__ function."""
    file_entry = os_file_entry.OSFileEntry(
        self._resolver_context, self._file_system, self._os_path_spec)

    self.assertIsNotNone(file_entry)

  # TODO: add tests for _GetDirectory
  # TODO: add tests for _GetLink
  # TODO: add tests for _GetStat
  # TODO: add tests for _GetSubFileEntries

  def testAccessTime(self):
    """Test the access_time property."""
    file_entry = os_file_entry.OSFileEntry(
        self._resolver_context, self._file_system, self._os_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.access_time)

  def testChangeTime(self):
    """Test the change_time property."""
    file_entry = os_file_entry.OSFileEntry(
        self._resolver_context, self._file_system, self._os_path_spec)

    self.assertIsNotNone(file_entry)
    # Not all operating systems provide a change time.
    _ = file_entry.change_time

  def testCreationTime(self):
    """Test the creation_time property."""
    file_entry = os_file_entry.OSFileEntry(
        self._resolver_context, self._file_system, self._os_path_spec)

    self.assertIsNotNone(file_entry)
    # Not all operating systems provide a creation time.
    _ = file_entry.creation_time

  def testModificationTime(self):
    """Test the modification_time property."""
    file_entry = os_file_entry.OSFileEntry(
        self._resolver_context, self._file_system, self._os_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.modification_time)

  def testName(self):
    """Test the name property."""
    file_entry = os_file_entry.OSFileEntry(
        self._resolver_context, self._file_system, self._os_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'testdir_os')

  def testSize(self):
    """Test the size property."""
    file_entry = os_file_entry.OSFileEntry(
        self._resolver_context, self._file_system, self._os_path_spec)

    self.assertIsNotNone(file_entry)
    # The size of a directory differs per operating system.
    _ = file_entry.size

  def testGetFileEntryByPathSpec(self):
    """Test the get a file entry by path specification functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._os_path_spec)

    self.assertIsNotNone(file_entry)

  # TODO: add tests for GetLinkedFileEntry

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    test_file = self._GetTestFilePath(['testdir_os', 'file1.txt'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, 'testdir_os')

  def testGetStat(self):
    """Tests the GetStat function."""
    test_file = self._GetTestFilePath(['testdir_os', 'file1.txt'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry.GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 6)

    # The date and time values are in a seconds precision and
    # cannot be predetermined.
    self.assertNotEqual(stat_object.atime, 0)
    self.assertNotEqual(stat_object.ctime, 0)
    self.assertNotEqual(stat_object.mtime, 0)

  def testIsFunctions(self):
    """Test the Is? functions."""
    test_file = self._GetTestFilePath(['testdir_os', 'file1.txt'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
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

    test_file = self._GetTestFilePath(['testdir_os'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertFalse(file_entry.IsRoot())
    self.assertFalse(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertTrue(file_entry.IsDirectory())
    self.assertFalse(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

  def testSubFileEntries(self):
    """Test the sub file entries iteration functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._os_path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 6)

    expected_sub_file_entry_names = [
        'file1.txt', 'file2.txt', 'file3.txt', 'file4.txt', 'file5.txt',
        'subdir1']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), expected_sub_file_entry_names)

  def testDataStreams(self):
    """Test the data streams functionality."""
    test_file = self._GetTestFilePath(['testdir_os', 'file1.txt'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    test_file = self._GetTestFilePath(['testdir_os'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    test_file = self._GetTestFilePath(['testdir_os', 'file1.txt'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
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
