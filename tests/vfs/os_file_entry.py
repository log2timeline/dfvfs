#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the operating system file entry implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import os_file_entry
from dfvfs.vfs import os_file_system

from tests import test_lib as shared_test_lib


class OSFileEntryTest(shared_test_lib.BaseTestCase):
  """Tests the operating system file entry."""

  # pylint: disable=protected-access

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['testdir_os'])
    self._SkipIfPathNotExists(test_path)

    self._os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    self._file_system = os_file_system.OSFileSystem(
        self._resolver_context, self._os_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testIntialize(self):
    """Test the __init__ function."""
    file_entry = os_file_entry.OSFileEntry(
        self._resolver_context, self._file_system, self._os_path_spec)

    self.assertIsNotNone(file_entry)

  def testGetAttributes(self):
    """Tests the _GetAttributes function."""
    test_path = self._GetTestFilePath(['testdir_os', 'file1.txt'])
    self._SkipIfPathNotExists(test_path)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertIsNone(file_entry._attributes)

    file_entry._GetAttributes()
    self.assertIsNotNone(file_entry._attributes)
    # Note that on some platforms this file can have extended attributes.
    self.assertGreaterEqual(len(file_entry._attributes), 0)

  # TODO: add tests for _GetDirectory
  # TODO: add tests for _GetLink

  def testGetStatAttribute(self):
    """Tests the _GetStatAttribute function."""
    test_path = self._GetTestFilePath(['testdir_os', 'file1.txt'])
    self._SkipIfPathNotExists(test_path)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_attribute = file_entry._GetStatAttribute()

    self.assertIsNotNone(stat_attribute)
    self.assertIsNotNone(stat_attribute.group_identifier)
    self.assertIsNotNone(stat_attribute.inode_number)
    self.assertIsNotNone(stat_attribute.mode)
    self.assertEqual(stat_attribute.number_of_links, 1)
    self.assertIsNotNone(stat_attribute.owner_identifier)
    self.assertEqual(stat_attribute.size, 6)
    self.assertEqual(stat_attribute.type, stat_attribute.TYPE_FILE)

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
    test_path = self._GetTestFilePath(['testdir_os', 'file1.txt'])
    self._SkipIfPathNotExists(test_path)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, 'testdir_os')

  def testIsFunctions(self):
    """Test the Is? functions."""
    test_path = self._GetTestFilePath(['testdir_os', 'file1.txt'])
    self._SkipIfPathNotExists(test_path)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
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

    test_path = self._GetTestFilePath(['testdir_os'])
    self._SkipIfPathNotExists(test_path)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
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
    test_path = self._GetTestFilePath(['testdir_os', 'file1.txt'])
    self._SkipIfPathNotExists(test_path)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    test_path = self._GetTestFilePath(['testdir_os'])
    self._SkipIfPathNotExists(test_path)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    test_path = self._GetTestFilePath(['testdir_os', 'file1.txt'])
    self._SkipIfPathNotExists(test_path)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
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
