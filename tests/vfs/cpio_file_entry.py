#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using the CPIOArchiveFile."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import cpio_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import cpio_file_entry
from dfvfs.vfs import cpio_file_system

from tests import test_lib as shared_test_lib


class CPIODirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the CPIO directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.bin.cpio'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._cpio_path_spec = cpio_path_spec.CPIOPathSpec(
        location='/syslog', parent=self._os_path_spec)

    self._file_system = cpio_file_system.CPIOFileSystem(self._resolver_context)
    self._file_system.Open(self._cpio_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = cpio_file_entry.CPIODirectory(
        self._file_system, self._cpio_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = cpio_file_entry.CPIODirectory(
        self._file_system, self._cpio_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 1)


class CPIOFileEntryTest(shared_test_lib.BaseTestCase):
  """Tests the CPIO extracted file entry."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.bin.cpio'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._cpio_path_spec = cpio_path_spec.CPIOPathSpec(
        location='/syslog', parent=self._os_path_spec)

    self._file_system = cpio_file_system.CPIOFileSystem(self._resolver_context)
    self._file_system.Open(self._cpio_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testIntialize(self):
    """Test the __init__ function."""
    file_entry = cpio_file_entry.CPIOFileEntry(
        self._resolver_context, self._file_system, self._cpio_path_spec)

    self.assertIsNotNone(file_entry)

  # TODO: test _GetDirectory
  # TODO: test _GetLink
  # TODO: test _GetStat
  # TODO: test _GetSubFileEntries

  def testModificationTime(self):
    """Test the modification_time property."""
    path_spec = cpio_path_spec.CPIOPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.modification_time)

  def testName(self):
    """Test the name property."""
    path_spec = cpio_path_spec.CPIOPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'syslog')

  def testSize(self):
    """Test the size property."""
    path_spec = cpio_path_spec.CPIOPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 1247)

  def testGetCPIOArchiveFileEntry(self):
    """Tests the GetCPIOArchiveFileEntry function."""
    path_spec = cpio_path_spec.CPIOPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    cpio_archive_file_entry = file_entry.GetCPIOArchiveFileEntry()
    self.assertIsNotNone(cpio_archive_file_entry)

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    path_spec = cpio_path_spec.CPIOPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertIsNotNone(parent_file_entry)
    self.assertEqual(parent_file_entry.name, '')

  def testGetStat(self):
    """Tests the GetStat function."""
    path_spec = cpio_path_spec.CPIOPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry.GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 1247)

    self.assertEqual(stat_object.mode, 436)
    self.assertEqual(stat_object.uid, 1000)
    self.assertEqual(stat_object.gid, 1000)

    self.assertEqual(stat_object.mtime, 1432702913)
    self.assertFalse(hasattr(stat_object, 'mtime_nano'))

  def testIsFunctions(self):
    """Test the Is? functions."""
    path_spec = cpio_path_spec.CPIOPathSpec(
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

    path_spec = cpio_path_spec.CPIOPathSpec(
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
    path_spec = cpio_path_spec.CPIOPathSpec(
        location='/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 1)

    expected_sub_file_entry_names = ['syslog']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))

  def testDataStreams(self):
    """Test the data streams functionality."""
    path_spec = cpio_path_spec.CPIOPathSpec(
        location='/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    path_spec = cpio_path_spec.CPIOPathSpec(
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
    path_spec = cpio_path_spec.CPIOPathSpec(
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
