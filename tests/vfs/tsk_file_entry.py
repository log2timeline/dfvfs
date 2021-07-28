#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using the SleuthKit (TSK)."""

import unittest

import pytsk3

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import attribute
from dfvfs.vfs import tsk_attribute
from dfvfs.vfs import tsk_file_entry
from dfvfs.vfs import tsk_file_system

from tests import test_lib as shared_test_lib


class TSKTimeTest(unittest.TestCase):
  """Tests for the SleuthKit timestamp."""

  def testCopyFromDateTimeString(self):
    """Tests the CopyFromDateTimeString function."""
    tsk_time_object = tsk_file_entry.TSKTime()

    if pytsk3.TSK_VERSION_NUM >= 0x040200ff:
      expected_fraction_of_second = 546875000
    else:
      expected_fraction_of_second = 5468750

    tsk_time_object.CopyFromDateTimeString('2010-08-12 21:06:31.546875')
    self.assertEqual(tsk_time_object.timestamp, 1281647191)
    self.assertEqual(
        tsk_time_object.fraction_of_second, expected_fraction_of_second)

  def testCopyToStatTimeTuple(self):
    """Tests the CopyToStatTimeTuple function."""
    if pytsk3.TSK_VERSION_NUM >= 0x040200ff:
      fraction_of_second = 546875000
    else:
      fraction_of_second = 5468750
    tsk_time_object = tsk_file_entry.TSKTime(
        fraction_of_second=fraction_of_second, timestamp=1281643591)

    stat_time_tuple = tsk_time_object.CopyToStatTimeTuple()
    self.assertEqual(stat_time_tuple, (1281643591, 5468750))

    tsk_time_object = tsk_file_entry.TSKTime()

    stat_time_tuple = tsk_time_object.CopyToStatTimeTuple()
    self.assertEqual(stat_time_tuple, (None, None))

  def testCopyToDateTimeString(self):
    """Tests the CopyToDateTimeString function."""
    if pytsk3.TSK_VERSION_NUM >= 0x040200ff:
      fraction_of_second = 546875000
    else:
      fraction_of_second = 5468750
    tsk_time_object = tsk_file_entry.TSKTime(
        fraction_of_second=fraction_of_second, timestamp=1281643591)

    if pytsk3.TSK_VERSION_NUM >= 0x040200ff:
      expected_date_time_string = '2010-08-12 20:06:31.546875000'
    else:
      expected_date_time_string = '2010-08-12 20:06:31.5468750'
    date_time_string = tsk_time_object.CopyToDateTimeString()
    self.assertEqual(date_time_string, expected_date_time_string)

    tsk_time_object = tsk_file_entry.TSKTime()

    date_time_string = tsk_time_object.CopyToDateTimeString()
    self.assertIsNone(date_time_string)

  def testGetDate(self):
    """Tests the GetDate function."""
    if pytsk3.TSK_VERSION_NUM >= 0x040200ff:
      fraction_of_second = 546875000
    else:
      fraction_of_second = 5468750
    tsk_time_object = tsk_file_entry.TSKTime(
        fraction_of_second=fraction_of_second, timestamp=1281643591)

    date_tuple = tsk_time_object.GetDate()
    self.assertEqual(date_tuple, (2010, 8, 12))

    tsk_time_object = tsk_file_entry.TSKTime()

    date_tuple = tsk_time_object.GetDate()
    self.assertEqual(date_tuple, (None, None, None))

  def testGetPlasoTimestamp(self):
    """Tests the GetPlasoTimestamp function."""
    tsk_time_object = tsk_file_entry.TSKTime(
        fraction_of_second=546875000, timestamp=1281643591)

    micro_posix_timestamp = tsk_time_object.GetPlasoTimestamp()
    self.assertEqual(micro_posix_timestamp, 1281643591546875)

    tsk_time_object = tsk_file_entry.TSKTime()

    micro_posix_timestamp = tsk_time_object.GetPlasoTimestamp()
    self.assertIsNone(micro_posix_timestamp)


# TODO: add tests for TSKDataStream


class TSKDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the TSK directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['ext2.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._tsk_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/',
        parent=self._raw_path_spec)

    self._file_system = tsk_file_system.TSKFileSystem(
        self._resolver_context, self._tsk_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = tsk_file_entry.TSKDirectory(
        self._file_system, self._tsk_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = tsk_file_entry.TSKDirectory(
        self._file_system, self._tsk_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 5)


class TSKFileEntryTestExt2(shared_test_lib.BaseTestCase):
  """Tests the SleuthKit (TSK) file entry on ext2."""

  # pylint: disable=protected-access

  _INODE_A_DIRECTORY = 12
  _INODE_A_FILE = 13
  _INODE_A_LINK = 16
  _INODE_ANOTHER_FILE = 15

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['ext2.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._tsk_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/',
        parent=self._raw_path_spec)

    self._file_system = tsk_file_system.TSKFileSystem(
        self._resolver_context, self._tsk_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    file_entry = tsk_file_entry.TSKFileEntry(
        self._resolver_context, self._file_system, self._tsk_path_spec)

    self.assertIsNotNone(file_entry)

  def testGetAttributes(self):
    """Tests the _GetAttributes function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_FILE,
        location='/a_directory/a_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertIsNone(file_entry._attributes)

    file_entry._GetAttributes()
    self.assertIsNotNone(file_entry._attributes)
    self.assertEqual(len(file_entry._attributes), 1)

    test_attribute = file_entry._attributes[0]
    self.assertIsInstance(test_attribute, attribute.StatAttribute)

    # No extended attributes are returned.
    # Also see: https://github.com/py4n6/pytsk/issues/79.

  # TODO: add tests for _GetDataStreams
  # TODO: add tests for _GetDirectory
  # TODO: add tests for _GetLink

  def testGetStat(self):
    """Tests the _GetStat function."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry._GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 22)

    self.assertEqual(stat_object.mode, 436)
    self.assertEqual(stat_object.uid, 1000)
    self.assertEqual(stat_object.gid, 1000)

    self.assertEqual(stat_object.atime, 1626962852)
    self.assertFalse(hasattr(stat_object, 'atime_nano'))

    self.assertEqual(stat_object.ctime, 1626962852)
    self.assertFalse(hasattr(stat_object, 'ctime_nano'))

    # EXT2 has no crtime timestamp.
    self.assertFalse(hasattr(stat_object, 'crtime'))
    self.assertFalse(hasattr(stat_object, 'crtime_nano'))

    self.assertEqual(stat_object.mtime, 1626962852)
    self.assertFalse(hasattr(stat_object, 'mtime_nano'))

  def testGetStatAttribute(self):
    """Tests the _GetStatAttribute function."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_attribute = file_entry._GetStatAttribute()

    self.assertIsNotNone(stat_attribute)
    self.assertEqual(stat_attribute.group_identifier, 1000)
    self.assertEqual(stat_attribute.inode_number, 15)
    self.assertEqual(stat_attribute.mode, 0o664)
    self.assertEqual(stat_attribute.number_of_links, 1)
    self.assertEqual(stat_attribute.owner_identifier, 1000)
    self.assertEqual(stat_attribute.size, 22)
    self.assertEqual(stat_attribute.type, stat_attribute.TYPE_FILE)

  # TODO: add tests for _GetSubFileEntries
  # TODO: add tests for _GetTimeValue
  # TODO: add tests for _TSKFileTimeCopyToStatTimeTuple

  def testAccessTime(self):
    """Test the access_time property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.access_time)

  def testBackupTime(self):
    """Test the backup_time property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.backup_time)

  def testChangeTime(self):
    """Test the change_time property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.change_time)

  def testCreationTime(self):
    """Test the creation_time property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.creation_time)

  def testDeletionTime(self):
    """Test the deletion_time property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.deletion_time)

  def testModificationTime(self):
    """Test the modification_time property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.modification_time)

  def testName(self):
    """Test the name property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'another_file')

  def testSize(self):
    """Test the size property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 22)

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)

  # TODO: add tests for GetFileObject

  def testGetLinkedFileEntry(self):
    """Tests the GetLinkedFileEntry function."""
    test_location = '/a_link'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_LINK,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    linked_file_entry = file_entry.GetLinkedFileEntry()

    self.assertIsNotNone(linked_file_entry)

    self.assertEqual(linked_file_entry.name, 'another_file')

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, 'a_directory')

  # TODO: add tests for GetTSKFile

  def testIsFunctions(self):
    """Tests the Is? functions."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
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
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        location=test_location, parent=self._raw_path_spec)
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

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/',
        parent=self._raw_path_spec)
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
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 5)

    # Note that passwords.txt~ is currently ignored by dfvfs, since
    # its directory entry has no pytsk3.TSK_FS_META object.
    expected_sub_file_entry_names = [
        'a_directory',
        'a_link',
        'lost+found',
        'passwords.txt',
        '$OrphanFiles']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))

    # Test a path specification without a location.
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 2)

  def testDataStreams(self):
    """Tests the data streams functionality."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    test_location = '/a_directory'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        location=test_location, parent=self._raw_path_spec)
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
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = ''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)


class TSKFileEntryTestFAT12(shared_test_lib.BaseTestCase):
  """Tests the SleuthKit (TSK) file entry on FAT-12."""

  # pylint: disable=protected-access

  _INODE_A_DIRECTORY = 5
  _INODE_A_FILE = 582
  _INODE_ANOTHER_FILE = 584

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['fat12.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._tsk_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/',
        parent=self._raw_path_spec)

    self._file_system = tsk_file_system.TSKFileSystem(
        self._resolver_context, self._tsk_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    file_entry = tsk_file_entry.TSKFileEntry(
        self._resolver_context, self._file_system, self._tsk_path_spec)

    self.assertIsNotNone(file_entry)

  def testGetAttributes(self):
    """Tests the _GetAttributes function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_FILE,
        location='/a_directory/a_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertIsNone(file_entry._attributes)

    file_entry._GetAttributes()
    self.assertIsNotNone(file_entry._attributes)
    self.assertEqual(len(file_entry._attributes), 1)

    test_attribute = file_entry._attributes[0]
    self.assertIsInstance(test_attribute, attribute.StatAttribute)

  # TODO: add tests for _GetDataStreams
  # TODO: add tests for _GetDirectory
  # TODO: add tests for _GetLink

  def testGetStat(self):
    """Tests the _GetStat function."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry._GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 22)

    self.assertEqual(stat_object.mode, 511)
    self.assertEqual(stat_object.uid, 0)
    self.assertEqual(stat_object.gid, 0)

    self.assertEqual(stat_object.atime, 1618704000)
    self.assertFalse(hasattr(stat_object, 'atime_nano'))

    # FAT has no ctime timestamp.
    self.assertFalse(hasattr(stat_object, 'ctime'))
    self.assertFalse(hasattr(stat_object, 'ctime_nano'))

    self.assertEqual(stat_object.crtime, 1618758550)
    self.assertFalse(hasattr(stat_object, 'crtime_nano'))

    self.assertEqual(stat_object.mtime, 1618758550)
    self.assertFalse(hasattr(stat_object, 'mtime_nano'))

  def testGetStatAttribute(self):
    """Tests the _GetStatAttribute function."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_attribute = file_entry._GetStatAttribute()

    self.assertIsNotNone(stat_attribute)
    self.assertEqual(stat_attribute.group_identifier, 0)
    self.assertEqual(stat_attribute.inode_number, 584)
    self.assertEqual(stat_attribute.mode, 0o777)
    self.assertEqual(stat_attribute.number_of_links, 1)
    self.assertEqual(stat_attribute.owner_identifier, 0)
    self.assertEqual(stat_attribute.size, 22)
    self.assertEqual(stat_attribute.type, stat_attribute.TYPE_FILE)

  # TODO: add tests for _GetSubFileEntries
  # TODO: add tests for _GetTimeValue
  # TODO: add tests for _TSKFileTimeCopyToStatTimeTuple

  def testAccessTime(self):
    """Test the access_time property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.access_time)

  def testBackupTime(self):
    """Test the backup_time property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.backup_time)

  def testChangeTime(self):
    """Test the change_time property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.change_time)

  def testCreationTime(self):
    """Test the creation_time property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.creation_time)

  def testDeletionTime(self):
    """Test the deletion_time property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.deletion_time)

  def testModificationTime(self):
    """Test the modification_time property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.modification_time)

  def testName(self):
    """Test the name property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'another_file')

  def testSize(self):
    """Test the size property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 22)

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)

  # TODO: add tests for GetFileObject
  # TODO: add tests for GetLinkedFileEntry

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, 'a_directory')

  # TODO: add tests for GetTSKFile

  def testIsFunctions(self):
    """Tests the Is? functions."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
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
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        location=test_location, parent=self._raw_path_spec)
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

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/',
        parent=self._raw_path_spec)
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
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 7)

    # Note that passwords.txt~ is currently ignored by dfvfs, since
    # its directory entry has no pytsk3.TSK_FS_META object.
    expected_sub_file_entry_names = [
        '$FAT1',
        '$FAT2',
        '$MBR',
        '$OrphanFiles',
        'FAT12_TEST  (Volume Label Entry)',
        'a_directory',
        'passwords.txt']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))

    # Test a path specification without a location.
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 2)

  def testDataStreams(self):
    """Tests the data streams functionality."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    test_location = '/a_directory'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        location=test_location, parent=self._raw_path_spec)
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
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = ''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)


class TSKFileEntryTestHFSPlus(shared_test_lib.BaseTestCase):
  """Tests the SleuthKit (TSK) file entry on HFS+."""

  # pylint: disable=protected-access

  _INODE_A_DIRECTORY = 18
  _INODE_A_FILE = 19
  _INODE_A_LINK = 24
  _INODE_ANOTHER_FILE = 23

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['hfsplus.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._tsk_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/',
        parent=self._raw_path_spec)

    self._file_system = tsk_file_system.TSKFileSystem(
        self._resolver_context, self._tsk_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    file_entry = tsk_file_entry.TSKFileEntry(
        self._resolver_context, self._file_system, self._tsk_path_spec)

    self.assertIsNotNone(file_entry)

  def testGetAttributes(self):
    """Tests the _GetAttributes function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_FILE,
        location='/a_directory/a_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertIsNone(file_entry._attributes)

    file_entry._GetAttributes()
    self.assertIsNotNone(file_entry._attributes)
    self.assertEqual(len(file_entry._attributes), 2)

    test_attribute = file_entry._attributes[0]
    self.assertIsInstance(test_attribute, attribute.StatAttribute)

    test_attribute = file_entry._attributes[1]
    self.assertIsInstance(test_attribute, tsk_attribute.TSKExtendedAttribute)
    self.assertEqual(test_attribute.name, 'myxattr')

    test_attribute_value_data = test_attribute.read()
    self.assertEqual(test_attribute_value_data, b'My extended attribute')

  # TODO: add tests for _GetDataStreams
  # TODO: add tests for _GetDirectory
  # TODO: add tests for _GetLink

  def testGetStat(self):
    """Tests the _GetStat function."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry._GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 22)

    self.assertEqual(stat_object.mode, 420)
    self.assertEqual(stat_object.uid, 501)
    self.assertEqual(stat_object.gid, 20)

    self.assertEqual(stat_object.atime, 1627013326)
    self.assertEqual(stat_object.atime_nano, 0)

    self.assertEqual(stat_object.ctime, 1627013326)
    self.assertEqual(stat_object.ctime_nano, 0)

    self.assertEqual(stat_object.crtime, 1627013326)
    self.assertEqual(stat_object.crtime_nano, 0)

    self.assertEqual(stat_object.mtime, 1627013326)
    self.assertEqual(stat_object.mtime_nano, 0)

  def testGetStatAttribute(self):
    """Tests the _GetStatAttribute function."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_attribute = file_entry._GetStatAttribute()

    self.assertIsNotNone(stat_attribute)
    self.assertEqual(stat_attribute.group_identifier, 20)
    self.assertEqual(stat_attribute.inode_number, 23)
    self.assertEqual(stat_attribute.mode, 0o644)
    self.assertEqual(stat_attribute.number_of_links, 1)
    self.assertEqual(stat_attribute.owner_identifier, 501)
    self.assertEqual(stat_attribute.size, 22)
    self.assertEqual(stat_attribute.type, stat_attribute.TYPE_FILE)

  # TODO: add tests for _GetSubFileEntries
  # TODO: add tests for _GetTimeValue
  # TODO: add tests for _TSKFileTimeCopyToStatTimeTuple

  def testAccessTime(self):
    """Test the access_time property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.access_time)

  def testBackupTime(self):
    """Test the backup_time property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.backup_time)

  def testChangeTime(self):
    """Test the change_time property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.change_time)

  def testCreationTime(self):
    """Test the creation_time property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.creation_time)

  def testDeletionTime(self):
    """Test the deletion_time property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.deletion_time)

  def testModificationTime(self):
    """Test the modification_time property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.modification_time)

  def testName(self):
    """Test the name property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'another_file')

  def testSize(self):
    """Test the size property."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 22)

  # TODO: add tests for GetFileObject

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)

  def testGetLinkedFileEntry(self):
    """Tests the GetLinkedFileEntry function."""
    test_location = '/a_link'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_LINK,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    linked_file_entry = file_entry.GetLinkedFileEntry()

    self.assertIsNotNone(linked_file_entry)

    self.assertEqual(linked_file_entry.name, 'another_file')

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, 'a_directory')

  # TODO: add tests for GetTSKFile

  def testIsFunctions(self):
    """Tests the Is? functions."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
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
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        location=test_location, parent=self._raw_path_spec)
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

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/',
        parent=self._raw_path_spec)
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
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 11)

    expected_sub_file_entry_names = [
        '$ExtentsFile',
        '$CatalogFile',
        '$BadBlockFile',
        '$AllocationFile',
        '$AttributesFile',
        '.fseventsd',
        '.HFS+ Private Directory Data\r',
        'a_directory',
        'a_link',
        'passwords.txt',
        '^^^^HFS+ Private Data']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))

    # Test a path specification without a location.
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 2)

  def testDataStreams(self):
    """Tests the data streams functionality."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    test_location = '/a_directory'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        location=test_location, parent=self._raw_path_spec)
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
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = ''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)


class TSKFileEntryTestNTFS(shared_test_lib.BaseTestCase):
  """Tests the SleuthKit (TSK) file entry on NTFS."""

  # pylint: disable=protected-access

  _MFT_ENTRY_A_DIRECTORY = 64
  _MFT_ENTRY_A_FILE = 65
  _MFT_ENTRY_ANOTHER_FILE = 67
  _MFT_ENTRY_PASSWORDS_TXT = 66

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['ntfs.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._tsk_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/',
        parent=self._raw_path_spec)

    self._file_system = tsk_file_system.TSKFileSystem(
        self._resolver_context, self._tsk_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testGetAttributes(self):
    """Tests the _GetAttributes function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_A_FILE,
        location='/a_directory/a_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry._attributes)

    file_entry._GetAttributes()
    self.assertIsNotNone(file_entry._attributes)
    self.assertEqual(len(file_entry._attributes), 5)

    test_attribute = file_entry._attributes[0]
    self.assertIsInstance(test_attribute, attribute.StatAttribute)

    test_attribute = file_entry._attributes[1]
    self.assertIsInstance(test_attribute, tsk_attribute.TSKAttribute)
    self.assertEqual(
        test_attribute.attribute_type, pytsk3.TSK_FS_ATTR_TYPE_NTFS_SI)

  # TODO: add tests for _GetDataStreams
  # TODO: add tests for _GetDirectory
  # TODO: add tests for _GetLink

  def testGetStat(self):
    """Tests the _GetStat function."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry._GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 22)

    self.assertEqual(stat_object.mode, 511)
    self.assertEqual(stat_object.uid, 48)
    self.assertEqual(stat_object.gid, 0)

    self.assertEqual(stat_object.atime, 1567246979)
    self.assertEqual(stat_object.atime_nano, 9602053)
    self.assertEqual(stat_object.ctime, 1567246979)
    self.assertEqual(stat_object.ctime_nano, 9611209)
    self.assertEqual(stat_object.crtime, 1567246979)
    self.assertEqual(stat_object.crtime_nano, 9602053)
    self.assertEqual(stat_object.mtime, 1567246979)
    self.assertEqual(stat_object.mtime_nano, 9611209)

  def testGetStatAttribute(self):
    """Tests the _GetStatAttribute function."""
    test_location = '/a_directory/another_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_ANOTHER_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_attribute = file_entry._GetStatAttribute()

    self.assertIsNotNone(stat_attribute)
    self.assertEqual(stat_attribute.group_identifier, 0)
    self.assertEqual(stat_attribute.inode_number, 67)
    self.assertEqual(stat_attribute.mode, 0o777)
    self.assertEqual(stat_attribute.number_of_links, 1)
    self.assertEqual(stat_attribute.owner_identifier, 48)
    self.assertEqual(stat_attribute.size, 22)
    self.assertEqual(stat_attribute.type, stat_attribute.TYPE_FILE)

  # TODO: add tests for _GetSubFileEntries
  # TODO: add tests for _GetTimeValue
  # TODO: add tests for _TSKFileTimeCopyToStatTimeTuple

  def testAccessTime(self):
    """Test the access_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_A_FILE,
        location='/a_directory/a_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.access_time)

  def testBackupTime(self):
    """Test the backup_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_A_FILE,
        location='/a_directory/a_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.backup_time)

  def testChangeTime(self):
    """Test the change_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_A_FILE,
        location='/a_directory/a_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.change_time)

  def testCreationTime(self):
    """Test the creation_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_A_FILE,
        location='/a_directory/a_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.creation_time)

  def testDeletionTime(self):
    """Test the deletion_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_A_FILE,
        location='/a_directory/a_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.deletion_time)

  def testModificationTime(self):
    """Test the modification_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_A_FILE,
        location='/a_directory/a_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.modification_time)

  def testName(self):
    """Test the name property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_A_FILE,
        location='/a_directory/a_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'a_file')

  def testSize(self):
    """Test the size property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_A_FILE,
        location='/a_directory/a_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 53)

  def testAttributes(self):
    """Tests the number_of_attributes property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_A_FILE,
        location='/a_directory/a_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_attributes, 5)

  def testDataStream(self):
    """Tests the number_of_data_streams and data_streams properties."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_A_FILE,
        location='/a_directory/a_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_A_DIRECTORY,
        location='/a_directory', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=10, location='/$UpCase',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 2)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    expected_data_stream_names = sorted(['', '$Info'])
    self.assertEqual(sorted(data_stream_names), expected_data_stream_names)

  def testGetDataStream(self):
    """Tests the retrieve data stream functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_A_FILE,
        location='/a_directory/a_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = ''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, data_stream_name)

    data_stream = file_entry.GetDataStream('bogus')
    self.assertIsNone(data_stream)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=10, location='/$UpCase',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = '$Info'
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, data_stream_name)


if __name__ == '__main__':
  unittest.main()
