#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using pyfsapfs."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import apfs_path_spec
from dfvfs.path import apfs_container_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import raw_path_spec
from dfvfs.path import tsk_partition_path_spec
from dfvfs.resolver import context
from dfvfs.resolver import resolver
from dfvfs.vfs import apfs_file_entry
from dfvfs.vfs import apfs_file_system

from tests import test_lib as shared_test_lib


class APFSDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the APFS directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['apfs.raw'])
    self._SkipIfPathNotExists(test_file)

    test_os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    test_raw_path_spec = raw_path_spec.RawPathSpec(parent=test_os_path_spec)
    self._apfs_container_path_spec = (
        apfs_container_path_spec.APFSContainerPathSpec(
            location='/apfs1', parent=test_raw_path_spec))
    self._apfs_path_spec = apfs_path_spec.APFSPathSpec(
        location='/', parent=self._apfs_container_path_spec)

    self._file_system = apfs_file_system.APFSFileSystem(self._resolver_context)
    self._file_system.Open(self._apfs_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = apfs_file_entry.APFSDirectory(
        self._file_system, self._apfs_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = apfs_file_entry.APFSDirectory(
        self._file_system, self._apfs_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 4)


class APFSFileEntryTest(shared_test_lib.BaseTestCase):
  """Tests the APFS file entry."""

  _IDENTIFIER_A_DIRECTORY = 18
  _IDENTIFIER_A_FILE = 19
  _IDENTIFIER_A_LINK = 22
  _IDENTIFIER_ANOTHER_FILE = 21

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['apfs.raw'])
    self._SkipIfPathNotExists(test_file)

    test_os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    test_raw_path_spec = raw_path_spec.RawPathSpec(parent=test_os_path_spec)
    self._apfs_container_path_spec = (
        apfs_container_path_spec.APFSContainerPathSpec(
            location='/apfs1', parent=test_raw_path_spec))
    self._apfs_path_spec = apfs_path_spec.APFSPathSpec(
        location='/', parent=self._apfs_container_path_spec)

    self._file_system = apfs_file_system.APFSFileSystem(self._resolver_context)
    self._file_system.Open(self._apfs_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    file_entry = apfs_file_entry.APFSFileEntry(
        self._resolver_context, self._file_system, self._apfs_path_spec)

    self.assertIsNotNone(file_entry)

  # TODO: add tests for _GetDirectory
  # TODO: add tests for _GetLink
  # TODO: add tests for _GetStat
  # TODO: add tests for _GetSubFileEntries

  def testAccessTime(self):
    """Test the access_time property."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.access_time)

  def testAddedTime(self):
    """Test the added_time property."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.added_time)

  def testChangeTime(self):
    """Test the change_time property."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.change_time)

  def testCreationTime(self):
    """Test the creation_time property."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.creation_time)

  def testModificationTime(self):
    """Test the modification_time property."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.modification_time)

  def testName(self):
    """Test the name property."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'another_file')

  def testSize(self):
    """Test the size property."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 22)

  def testGetAPFSFileEntry(self):
    """Tests the GetAPFSFileEntry function."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    fsafps_file_entry = file_entry.GetAPFSFileEntry()
    self.assertIsNotNone(fsafps_file_entry)

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_A_FILE,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)

  def testGetLinkedFileEntry(self):
    """Tests the GetLinkedFileEntry function."""
    test_location = '/a_link'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_A_LINK, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    linked_file_entry = file_entry.GetLinkedFileEntry()

    self.assertIsNotNone(linked_file_entry)

    self.assertEqual(linked_file_entry.name, 'another_file')

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, 'a_directory')

  def testGetStat(self):
    """Tests the GetStat function."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry.GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 22)

    self.assertEqual(stat_object.mode, 420)
    self.assertEqual(stat_object.uid, 99)
    self.assertEqual(stat_object.gid, 99)

    self.assertEqual(stat_object.atime, 1596950905)
    self.assertEqual(stat_object.atime_nano, 6246998)

    self.assertEqual(stat_object.ctime, 1596950905)
    self.assertEqual(stat_object.ctime_nano, 6267234)

    self.assertEqual(stat_object.crtime, 1596950905)
    self.assertEqual(stat_object.crtime_nano, 6267234)

    self.assertEqual(stat_object.mtime, 1596950905)
    self.assertEqual(stat_object.mtime_nano, 6246998)

  def testIsFunctions(self):
    """Tests the Is? functions."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
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
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_A_DIRECTORY, location=test_location,
        parent=self._apfs_container_path_spec)
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

    path_spec = apfs_path_spec.APFSPathSpec(
        location='/', parent=self._apfs_container_path_spec)
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
    path_spec = apfs_path_spec.APFSPathSpec(
        location='/', parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 4)

    expected_sub_file_entry_names = [
        '.fseventsd',
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
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_A_DIRECTORY,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 2)

  def testDataStreams(self):
    """Tests the data streams functionality."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    test_location = '/a_directory'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_A_DIRECTORY, location=test_location,
        parent=self._apfs_container_path_spec)
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
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = ''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)


class APFSFileEntryTestEncrypted(shared_test_lib.BaseTestCase):
  """Tests the APFS file entry on an encrypted file system."""

  _APFS_PASSWORD = 'apfs-TEST'

  _IDENTIFIER_A_DIRECTORY = 18
  _IDENTIFIER_A_LINK = 22
  _IDENTIFIER_ANOTHER_FILE = 21

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['apfs_encrypted.dmg'])
    self._SkipIfPathNotExists(test_file)

    test_os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    test_raw_path_spec = raw_path_spec.RawPathSpec(parent=test_os_path_spec)
    partition_path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p1', parent=test_raw_path_spec)
    self._apfs_container_path_spec = (
        apfs_container_path_spec.APFSContainerPathSpec(
            location='/apfs1', parent=partition_path_spec))
    self._apfs_path_spec = apfs_path_spec.APFSPathSpec(
        location='/', parent=self._apfs_container_path_spec)

    resolver.Resolver.key_chain.SetCredential(
        self._apfs_container_path_spec, 'password', self._APFS_PASSWORD)

    self._file_system = apfs_file_system.APFSFileSystem(self._resolver_context)
    self._file_system.Open(self._apfs_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    file_entry = apfs_file_entry.APFSFileEntry(
        self._resolver_context, self._file_system, self._apfs_path_spec)

    self.assertIsNotNone(file_entry)

  # TODO: add tests for _GetDirectory
  # TODO: add tests for _GetLink
  # TODO: add tests for _GetStat
  # TODO: add tests for _GetSubFileEntries

  def testAccessTime(self):
    """Test the access_time property."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.access_time)

  def testChangeTime(self):
    """Test the change_time property."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.change_time)

  def testCreationTime(self):
    """Test the creation_time property."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.creation_time)

  def testModificationTime(self):
    """Test the modification_time property."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.modification_time)

  def testName(self):
    """Test the name property."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'another_file')

  def testSize(self):
    """Test the size property."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 22)

  def testGetAPFSFileEntry(self):
    """Tests the GetAPFSFileEntry function."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    fsafps_file_entry = file_entry.GetAPFSFileEntry()
    self.assertIsNotNone(fsafps_file_entry)

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=20, parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)

  def testGetLinkedFileEntry(self):
    """Tests the GetLinkedFileEntry function."""
    test_location = '/a_link'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_A_LINK, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    linked_file_entry = file_entry.GetLinkedFileEntry()

    self.assertIsNotNone(linked_file_entry)

    self.assertEqual(linked_file_entry.name, 'a_file')

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, 'a_directory')

  def testGetStat(self):
    """Tests the GetStat function."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry.GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 22)

    self.assertEqual(stat_object.mode, 420)
    self.assertEqual(stat_object.uid, 99)
    self.assertEqual(stat_object.gid, 99)

    self.assertEqual(stat_object.atime, 1539321508)
    self.assertEqual(stat_object.atime_nano, 9478457)

    self.assertEqual(stat_object.ctime, 1539321508)
    self.assertEqual(stat_object.ctime_nano, 9495127)

    self.assertEqual(stat_object.crtime, 1539321508)
    self.assertEqual(stat_object.crtime_nano, 9495127)

    self.assertEqual(stat_object.mtime, 1539321508)
    self.assertEqual(stat_object.mtime_nano, 9478457)

  def testIsFunctions(self):
    """Tests the Is? functions."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
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
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_A_DIRECTORY, location=test_location,
        parent=self._apfs_container_path_spec)
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

    path_spec = apfs_path_spec.APFSPathSpec(
        location='/', parent=self._apfs_container_path_spec)
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
    path_spec = apfs_path_spec.APFSPathSpec(
        location='/', parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 4)

    expected_sub_file_entry_names = [
        '.fseventsd',
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

  def testDataStreams(self):
    """Tests the data streams functionality."""
    test_location = '/a_directory/another_file'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    test_location = '/a_directory'
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_A_DIRECTORY, location=test_location,
        parent=self._apfs_container_path_spec)
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
    path_spec = apfs_path_spec.APFSPathSpec(
        identifier=self._IDENTIFIER_ANOTHER_FILE, location=test_location,
        parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = ''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)


if __name__ == '__main__':
  unittest.main()
