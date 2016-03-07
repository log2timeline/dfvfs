#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using the SleuthKit (TSK)."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import tsk_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import tsk_file_entry
from dfvfs.vfs import tsk_file_system


class TSKFileEntryTestExt2(unittest.TestCase):
  """The unit test for the SleuthKit (TSK) file entry object on ext2."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'ímynd.dd')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._tsk_path_spec = tsk_path_spec.TSKPathSpec(
        location=u'/', parent=self._os_path_spec)

    self._file_system = tsk_file_system.TSKFileSystem(self._resolver_context)
    self._file_system.Open(self._tsk_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()

  def testIntialize(self):
    """Test the initialize functionality."""
    file_entry = tsk_file_entry.TSKFileEntry(
        self._resolver_context, self._file_system, self._tsk_path_spec)

    self.assertIsNotNone(file_entry)

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    path_spec = tsk_path_spec.TSKPathSpec(inode=15, parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)

  def testGetLinkedFileEntry(self):
    """Tests the GetLinkedFileEntry function."""
    test_location = u'/a_link'
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=13, location=test_location, parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    linked_file_entry = file_entry.GetLinkedFileEntry()

    self.assertIsNotNone(linked_file_entry)

    self.assertEqual(linked_file_entry.name, u'another_file')

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    test_location = u'/a_directory/another_file'
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=16, location=test_location, parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, u'a_directory')

  def testGetStat(self):
    """Tests the GetStat function."""
    test_location = u'/a_directory/another_file'
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=16, location=test_location, parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry.GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 22)

    self.assertEqual(stat_object.mode, 384)
    self.assertEqual(stat_object.uid, 151107)
    self.assertEqual(stat_object.gid, 5000)

    self.assertEqual(stat_object.atime, 1337961563)
    self.assertEqual(stat_object.atime_nano, 0)
    self.assertEqual(stat_object.ctime, 1337961563)
    self.assertEqual(stat_object.ctime_nano, 0)
    self.assertEqual(stat_object.mtime, 1337961563)
    self.assertEqual(stat_object.mtime_nano, 0)

  def testIsFunctions(self):
    """Test the Is? functions."""
    test_location = u'/a_directory/another_file'
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=16, location=test_location, parent=self._os_path_spec)
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

    test_location = u'/a_directory'
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=12, location=test_location, parent=self._os_path_spec)
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

    path_spec = tsk_path_spec.TSKPathSpec(
        location=u'/', parent=self._os_path_spec)
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
    """Test the sub file entries iteration functionality."""
    path_spec = tsk_path_spec.TSKPathSpec(
        location=u'/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 5)

    # Note that passwords.txt~ is currently ignored by dfvfs, since
    # its directory entry has no pytsk3.TSK_FS_META object.
    expected_sub_file_entry_names = [
        u'a_directory',
        u'a_link',
        u'lost+found',
        u'passwords.txt',
        u'$OrphanFiles']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))

  def testDataStreams(self):
    """Test the data streams functionality."""
    test_location = u'/a_directory/another_file'
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=16, location=test_location, parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [u''])

    test_location = u'/a_directory'
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=12, location=test_location, parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    test_location = u'/a_directory/another_file'
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=16, location=test_location, parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = u''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)


class TSKFileEntryTestHFS(unittest.TestCase):
  """The unit test for the SleuthKit (TSK) file entry object on HFS."""

  # TODO: implement.



class TSKFileEntryTestNTFS(unittest.TestCase):
  """The unit test for the SleuthKit (TSK) file entry object on NTFS."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'vsstest.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    self._tsk_path_spec = tsk_path_spec.TSKPathSpec(
        location=u'\\', parent=self._qcow_path_spec)

    self._file_system = tsk_file_system.TSKFileSystem(self._resolver_context)
    self._file_system.Open(self._tsk_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()

  def testGetStat(self):
    """Tests the GetStat function."""
    test_location = (
        u'\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=38, location=test_location, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry.GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 65536)

    self.assertEqual(stat_object.mode, 365)
    self.assertEqual(stat_object.uid, 0)
    self.assertEqual(stat_object.gid, 0)

    self.assertEqual(stat_object.atime, 1386052509)
    self.assertEqual(stat_object.atime_nano, 5023783)
    self.assertEqual(stat_object.ctime, 1386052509)
    self.assertEqual(stat_object.ctime_nano, 5179783)
    self.assertEqual(stat_object.crtime, 1386052509)
    self.assertEqual(stat_object.crtime_nano, 5023783)
    self.assertEqual(stat_object.mtime, 1386052509)
    self.assertEqual(stat_object.mtime_nano, 5179783)

  def testAttributes(self):
    """Test the attributes functionality."""
    test_location = (
        u'\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=38, location=test_location, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_attributes, 4)

  def testDataStream(self):
    """Test the data streams functionality."""
    test_location = (
        u'\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=38, location=test_location, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [u''])

    path_spec = tsk_path_spec.TSKPathSpec(
        inode=36, location=u'\\System Volume Information',
        parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

    test_location = u'\\$Extend\\$RmMetadata\\$Repair'
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=28, location=test_location, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 2)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(sorted(data_stream_names), sorted([u'', u'$Config']))

  def testGetDataStream(self):
    """Test the retrieve data stream functionality."""
    test_location = (
        u'\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=38, location=test_location, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = u''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, data_stream_name)

    data_stream = file_entry.GetDataStream(u'bogus')
    self.assertIsNone(data_stream)

    test_location = u'\\$Extend\\$RmMetadata\\$Repair'
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=28, location=test_location, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = u'$Config'
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, data_stream_name)


if __name__ == '__main__':
  unittest.main()
