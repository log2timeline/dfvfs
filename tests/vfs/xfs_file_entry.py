#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using pyfsext."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import xfs_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import raw_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import xfs_file_entry
from dfvfs.vfs import xfs_file_system

from tests import test_lib as shared_test_lib


# TODO: add tests for XFSDirectory.


class XFSFileEntryTest(shared_test_lib.BaseTestCase):
  """Tests the XFS file entry."""

  _INODE_A_DIRECTORY = 11075
  _INODE_A_FILE = 11076
  _INODE_A_LINK = 11079
  _INODE_ANOTHER_FILE = 11078

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['xfs.raw'])
    self._SkipIfPathNotExists(test_file)

    test_os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._raw_path_spec = raw_path_spec.RawPathSpec(parent=test_os_path_spec)
    self._xfs_path_spec = xfs_path_spec.XFSPathSpec(
        location='/', parent=self._raw_path_spec)

    self._file_system = xfs_file_system.XFSFileSystem(self._resolver_context)
    self._file_system.Open(self._xfs_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    file_entry = xfs_file_entry.XFSFileEntry(
        self._resolver_context, self._file_system, self._xfs_path_spec)

    self.assertIsNotNone(file_entry)

  def testAccessTime(self):
    """Test the access_time property."""
    test_location = '/a_directory/another_file'
    path_spec = xfs_path_spec.XFSPathSpec(
        inode=self._INODE_ANOTHER_FILE, location=test_location,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.access_time)

  def testChangeTime(self):
    """Test the change_time property."""
    test_location = '/a_directory/another_file'
    path_spec = xfs_path_spec.XFSPathSpec(
        inode=self._INODE_ANOTHER_FILE, location=test_location,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.change_time)

  def testCreationTime(self):
    """Test the creation_time property."""
    test_location = '/a_directory/another_file'
    path_spec = xfs_path_spec.XFSPathSpec(
        inode=self._INODE_ANOTHER_FILE, location=test_location,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.creation_time)

  def testModificationTime(self):
    """Test the modification_time property."""
    test_location = '/a_directory/another_file'
    path_spec = xfs_path_spec.XFSPathSpec(
        inode=self._INODE_ANOTHER_FILE, location=test_location,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.modification_time)

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    path_spec = xfs_path_spec.XFSPathSpec(
        inode=self._INODE_A_FILE, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)

  def testGetLinkedFileEntry(self):
    """Tests the GetLinkedFileEntry function."""
    test_location = '/a_link'
    path_spec = xfs_path_spec.XFSPathSpec(
        inode=self._INODE_A_LINK, location=test_location,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    linked_file_entry = file_entry.GetLinkedFileEntry()

    self.assertIsNotNone(linked_file_entry)

    self.assertEqual(linked_file_entry.name, 'another_file')

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    test_location = '/a_directory/another_file'
    path_spec = xfs_path_spec.XFSPathSpec(
        inode=self._INODE_ANOTHER_FILE, location=test_location,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, 'a_directory')

  def testGetStat(self):
    """Tests the GetStat function."""
    test_location = '/a_directory/another_file'
    path_spec = xfs_path_spec.XFSPathSpec(
        inode=self._INODE_ANOTHER_FILE, location=test_location,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry.GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 22)

    self.assertEqual(stat_object.mode, 436)
    self.assertEqual(stat_object.uid, 1000)
    self.assertEqual(stat_object.gid, 1000)

    self.assertEqual(stat_object.atime, 1605204173)
    self.assertEqual(stat_object.atime_nano, 7637974)

    self.assertEqual(stat_object.ctime, 1605204173)
    self.assertEqual(stat_object.ctime_nano, 7637974)

    self.assertEqual(stat_object.crtime, 1605204173)
    self.assertEqual(stat_object.crtime_nano, 7637974)

    self.assertEqual(stat_object.mtime, 1605204173)
    self.assertEqual(stat_object.mtime_nano, 7637974)

  def testIsFunctions(self):
    """Tests the Is? functions."""
    test_location = '/a_directory/another_file'
    path_spec = xfs_path_spec.XFSPathSpec(
        inode=self._INODE_ANOTHER_FILE, location=test_location,
        parent=self._raw_path_spec)
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

    test_location = '/a_directory'
    path_spec = xfs_path_spec.XFSPathSpec(
        inode=self._INODE_A_DIRECTORY, location=test_location,
        parent=self._raw_path_spec)
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

    path_spec = xfs_path_spec.XFSPathSpec(
        location='/', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertTrue(file_entry.IsRoot())
    self.assertFalse(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertTrue(file_entry.IsDirectory())
    self.assertFalse(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

  def testSubFileEntries(self):
    """Tests the number_of_sub_file_entries and sub_file_entries properties."""
    path_spec = xfs_path_spec.XFSPathSpec(
        location='/', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 3)

    expected_sub_file_entry_names = [
        'a_directory',
        'a_link',
        'passwords.txt']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))

    # Test a path specification without a location.
    path_spec = xfs_path_spec.XFSPathSpec(
        inode=self._INODE_A_DIRECTORY, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 2)

  def testDataStreams(self):
    """Tests the data streams functionality."""
    test_location = '/a_directory/another_file'
    path_spec = xfs_path_spec.XFSPathSpec(
        inode=self._INODE_ANOTHER_FILE, location=test_location,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    test_location = '/a_directory'
    path_spec = xfs_path_spec.XFSPathSpec(
        inode=self._INODE_A_DIRECTORY, location=test_location,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    test_location = '/a_directory/another_file'
    path_spec = xfs_path_spec.XFSPathSpec(
        inode=self._INODE_ANOTHER_FILE, location=test_location,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = ''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)


if __name__ == '__main__':
  unittest.main()
