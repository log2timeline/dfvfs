#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using the tarfile."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import tar_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import tar_file_entry
from dfvfs.vfs import tar_file_system

from tests import test_lib as shared_test_lib


class TARDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the TAR extracted directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.tar'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._tar_path_spec = tar_path_spec.TARPathSpec(
        location='/', parent=self._os_path_spec)

    self._file_system = tar_file_system.TARFileSystem(self._resolver_context)
    self._file_system.Open(self._tar_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = tar_file_entry.TARDirectory(
        self._file_system, self._tar_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = tar_file_entry.TARDirectory(
        self._file_system, self._tar_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 1)


class TARFileEntryTest(shared_test_lib.BaseTestCase):
  """Tests the TAR extracted file entry."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.tar'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._tar_path_spec = tar_path_spec.TARPathSpec(
        location='/syslog', parent=self._os_path_spec)

    self._file_system = tar_file_system.TARFileSystem(self._resolver_context)
    self._file_system.Open(self._tar_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testIntialize(self):
    """Test the __init__ function."""
    file_entry = tar_file_entry.TARFileEntry(
        self._resolver_context, self._file_system, self._tar_path_spec)

    self.assertIsNotNone(file_entry)

  # TODO: add tests for _GetDirectory
  # TODO: add tests for _GetLink
  # TODO: add tests for _GetStat
  # TODO: add tests for _GetSubFileEntries

  def testModificationTime(self):
    """Test the modification_time property."""
    file_entry = tar_file_entry.TARFileEntry(
        self._resolver_context, self._file_system, self._tar_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.modification_time)

  def testName(self):
    """Test the name property."""
    file_entry = tar_file_entry.TARFileEntry(
        self._resolver_context, self._file_system, self._tar_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'syslog')

  def testSize(self):
    """Test the size property."""
    file_entry = tar_file_entry.TARFileEntry(
        self._resolver_context, self._file_system, self._tar_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 1247)

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    path_spec = tar_path_spec.TARPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertIsNotNone(parent_file_entry)
    self.assertEqual(parent_file_entry.name, '')

  def testGetStat(self):
    """Tests the GetStat function."""
    path_spec = tar_path_spec.TARPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry.GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 1247)

    self.assertEqual(stat_object.mode, 256)
    self.assertEqual(stat_object.uid, 151107)
    self.assertEqual(stat_object.gid, 5000)

    self.assertEqual(stat_object.mtime, 1343166324)
    self.assertFalse(hasattr(stat_object, 'mtime_nano'))

  # TODO: add tests for GetTARInfo

  def testIsFunctions(self):
    """Test the Is? functions."""
    path_spec = tar_path_spec.TARPathSpec(
        location='/syslog', parent=self._os_path_spec)
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

    path_spec = tar_path_spec.TARPathSpec(
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
    path_spec = tar_path_spec.TARPathSpec(
        location='/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self._assertSubFileEntries(file_entry, ['syslog'])

    # Test on a tar file that has missing directory entries.
    test_file = self._GetTestFilePath(['missing_directory_entries.tar'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = tar_path_spec.TARPathSpec(location='/', parent=path_spec)

    file_system = tar_file_system.TARFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)
    file_system.Open(path_spec)

    file_entry = file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self._assertSubFileEntries(
        file_entry, ['File System', 'Non Missing Directory Entry'])

    file_system_sub_file_entry = None
    for sub_file_entry in file_entry.sub_file_entries:
      # The "File System" and its sub-directories have missing entries within
      # the tar file, but still should be found due to the AssetManifest.plist
      # file found within the directories.
      if sub_file_entry.name == 'File System':
        self.assertTrue(sub_file_entry.IsVirtual())

        self._assertSubFileEntries(sub_file_entry, ['Recordings'])

        file_system_sub_file_entry = sub_file_entry

      else:
        self._assertSubFileEntries(sub_file_entry, ['test_file.txt'])

    if file_system_sub_file_entry:
      for sub_file_entry in file_system_sub_file_entry.sub_file_entries:
        self.assertTrue(sub_file_entry.IsVirtual())

        self._assertSubFileEntries(sub_file_entry, ['AssetManifest.plist'])

    file_system.Close()

  def testDataStreams(self):
    """Test the data streams functionality."""
    path_spec = tar_path_spec.TARPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    path_spec = tar_path_spec.TARPathSpec(
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
    path_spec = tar_path_spec.TARPathSpec(
        location='/syslog', parent=self._os_path_spec)
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
