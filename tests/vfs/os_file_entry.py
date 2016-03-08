#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the operating system file entry implementation."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import os_file_entry
from dfvfs.vfs import os_file_system


class OSFileEntryTest(unittest.TestCase):
  """The unit test for the operating system file entry object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'testdir_os')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)

    self._file_system = os_file_system.OSFileSystem(self._resolver_context)
    self._file_system.Open(self._os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()

  def testIntialize(self):
    """Test the initialize functionality."""
    file_entry = os_file_entry.OSFileEntry(
        self._resolver_context, self._file_system, self._os_path_spec)

    self.assertIsNotNone(file_entry)

  def testGetFileEntryByPathSpec(self):
    """Test the get a file entry by path specification functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._os_path_spec)

    self.assertIsNotNone(file_entry)

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    test_file = os.path.join(u'test_data', u'testdir_os', u'file1.txt')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, u'testdir_os')

  def testGetStat(self):
    """Tests the GetStat function."""
    test_file = os.path.join(u'test_data', u'testdir_os', u'file1.txt')
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
    test_file = os.path.join(u'test_data', u'testdir_os', u'file1.txt')
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

    test_file = os.path.join(u'test_data', u'testdir_os')
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
        u'file1.txt', u'file2.txt', u'file3.txt', u'file4.txt', u'file5.txt',
        u'subdir1']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), expected_sub_file_entry_names)

  def testDataStreams(self):
    """Test the data streams functionality."""
    test_file = os.path.join('test_data', 'testdir_os', 'file1.txt')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [u''])

    test_file = os.path.join('test_data', 'testdir_os')
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
    test_file = os.path.join('test_data', 'testdir_os', 'file1.txt')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = u''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, data_stream_name)

    data_stream = file_entry.GetDataStream(u'bogus')
    self.assertIsNone(data_stream)


if __name__ == '__main__':
  unittest.main()
