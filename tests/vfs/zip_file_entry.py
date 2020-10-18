#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using the zipfile."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import zip_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import zip_file_entry
from dfvfs.vfs import zip_file_system

from tests import test_lib as shared_test_lib


class ZIPDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the ZIP extracted file directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.zip'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._zip_path_spec = zip_path_spec.ZipPathSpec(
        location='/', parent=self._os_path_spec)

    self._file_system = zip_file_system.ZipFileSystem(self._resolver_context)
    self._file_system.Open(self._zip_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = zip_file_entry.ZIPDirectory(
        self._file_system, self._zip_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = zip_file_entry.ZIPDirectory(
        self._file_system, self._zip_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 2)


class ZIPFileEntryTest(shared_test_lib.BaseTestCase):
  """Tests the ZIP extracted file entry."""

  # pylint: disable=protected-access

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.zip'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._zip_path_spec = zip_path_spec.ZipPathSpec(
        location='/', parent=self._os_path_spec)

    self._file_system = zip_file_system.ZipFileSystem(self._resolver_context)
    self._file_system.Open(self._zip_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testIntialize(self):
    """Test the __init__ function."""
    file_entry = zip_file_entry.ZipFileEntry(
        self._resolver_context, self._file_system, self._zip_path_spec,
        is_virtual=True)

    self.assertIsNotNone(file_entry)

  # TODO: add tests for _GetDirectory function.

  def testGetStat(self):
    """Tests the _GetStat function."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry._GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 1247)

    self.assertEqual(stat_object.mode, 256)

    self.assertEqual(stat_object.mtime, 1343141124)
    # TODO: re-enable when dfdatetime updates are committed
    # self.assertEqual(stat_object.mtime_nano, None)

  # TODO: add tests for _GetSubFileEntries

  def testAccessTime(self):
    """Test the access_time property."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.access_time)

  def testChangeTime(self):
    """Test the change_time property."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.change_time)

  def testCreationTime(self):
    """Test the creation_time property."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.creation_time)

  def testDataStreams(self):
    """Test the data_streams property."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    path_spec = zip_path_spec.ZipPathSpec(
        location='/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

  def testModificationTime(self):
    """Test the modification_time property."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry.modification_time)

  def testName(self):
    """Test the name property."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'syslog')

  def testSize(self):
    """Test the size property."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 1247)

  def testSubFileEntries(self):
    """Test the sub_file_entries property."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.number_of_sub_file_entries, 2)

    self._assertSubFileEntries(file_entry, ['syslog', 'wtmp.1'])

    # Test on a zip file that has missing directory entries.
    test_file = self._GetTestFilePath(['missing_directory_entries.zip'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = zip_path_spec.ZipPathSpec(location='/', parent=path_spec)

    file_system = zip_file_system.ZipFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)
    file_system.Open(path_spec)

    file_entry = file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self._assertSubFileEntries(file_entry, ['folder'])

    # The "folder" folder is a missing directory entry but should still
    # be found due to the files found inside the directory.
    sub_file_entry = next(file_entry.sub_file_entries)
    self.assertTrue(sub_file_entry.IsVirtual())
    self._assertSubFileEntries(sub_file_entry, ['syslog', 'wtmp.1'])

    file_system.Close()

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = ''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, data_stream_name)

    data_stream = file_entry.GetDataStream('bogus')
    self.assertIsNone(data_stream)

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, '')

  # TODO: add tests for GetZipInfo function.

  def testIsAllocated(self):
    """Test the IsAllocated function."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsAllocated())

    path_spec = zip_path_spec.ZipPathSpec(
        location='/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsAllocated())

  def testIsDevice(self):
    """Test the IsDevice function."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsDevice())

    path_spec = zip_path_spec.ZipPathSpec(
        location='/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsDevice())

  def testIsDirectory(self):
    """Test the IsDirectory function."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsDirectory())

    path_spec = zip_path_spec.ZipPathSpec(
        location='/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsDirectory())

  def testIsFile(self):
    """Test the IsFile function."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsFile())

    path_spec = zip_path_spec.ZipPathSpec(
        location='/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsFile())

  def testIsLink(self):
    """Test the IsLink function."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsLink())

    path_spec = zip_path_spec.ZipPathSpec(
        location='/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsLink())

  def testIsPipe(self):
    """Test the IsPipe function."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsPipe())

    path_spec = zip_path_spec.ZipPathSpec(
        location='/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsPipe())

  def testIsRoot(self):
    """Test the IsRoot function."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsRoot())

    path_spec = zip_path_spec.ZipPathSpec(
        location='/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsRoot())

  def testIsSocket(self):
    """Test the IsSocket function."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsSocket())

    path_spec = zip_path_spec.ZipPathSpec(
        location='/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsSocket())

  def testIsVirtual(self):
    """Test the IsVirtual function."""
    path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsVirtual())

    path_spec = zip_path_spec.ZipPathSpec(
        location='/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsVirtual())

  # TODO: add tests for GetZipInfo function.


if __name__ == '__main__':
  unittest.main()
