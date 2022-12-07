#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using the SleuthKit (TSK)."""

import decimal
import unittest

import pytsk3

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import tsk_attribute
from dfvfs.vfs import tsk_file_entry
from dfvfs.vfs import tsk_file_system

from tests import test_lib as shared_test_lib


class TSKTimeTest(unittest.TestCase):
  """Tests for the SleuthKit timestamp."""

  # pylint: disable=protected-access

  def testGetNormalizedTimestamp(self):
    """Tests the _GetNormalizedTimestamp function."""
    if pytsk3.TSK_VERSION_NUM >= 0x040200ff:
      fraction_of_second = 546875000
    else:
      fraction_of_second = 5468750

    tsk_time_object = tsk_file_entry.TSKTime(
        fraction_of_second=fraction_of_second, timestamp=1281643591)

    normalized_timestamp = tsk_time_object._GetNormalizedTimestamp()
    self.assertEqual(
        normalized_timestamp, decimal.Decimal('1281643591.546875'))

    tsk_time_object = tsk_file_entry.TSKTime(
        fraction_of_second=fraction_of_second, time_zone_offset=60,
        timestamp=1281643591)

    normalized_timestamp = tsk_time_object._GetNormalizedTimestamp()
    self.assertEqual(
        normalized_timestamp, decimal.Decimal('1281639991.546875'))

    tsk_time_object = tsk_file_entry.TSKTime(
        fraction_of_second=fraction_of_second, timestamp=1281643591)
    tsk_time_object.time_zone_offset = 60

    normalized_timestamp = tsk_time_object._GetNormalizedTimestamp()
    self.assertEqual(
        normalized_timestamp, decimal.Decimal('1281639991.546875'))

    tsk_time_object = tsk_file_entry.TSKTime()

    normalized_timestamp = tsk_time_object._GetNormalizedTimestamp()
    self.assertIsNone(normalized_timestamp)

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

    tsk_time_object.CopyFromDateTimeString('2010-08-12 21:06:31.546875-01:00')
    self.assertEqual(tsk_time_object.timestamp, 1281647191)
    self.assertEqual(tsk_time_object._time_zone_offset, -60)

    tsk_time_object.CopyFromDateTimeString('2010-08-12 21:06:31.546875+01:00')
    self.assertEqual(tsk_time_object._timestamp, 1281647191)
    self.assertEqual(tsk_time_object._time_zone_offset, 60)

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
    if pytsk3.TSK_VERSION_NUM >= 0x040200ff:
      fraction_of_second = 546875000
    else:
      fraction_of_second = 5468750

    tsk_time_object = tsk_file_entry.TSKTime(
        fraction_of_second=fraction_of_second, timestamp=1281643591)

    micro_posix_timestamp = tsk_time_object.GetPlasoTimestamp()
    self.assertEqual(micro_posix_timestamp, 1281643591546875)

    tsk_time_object = tsk_file_entry.TSKTime()

    micro_posix_timestamp = tsk_time_object.GetPlasoTimestamp()
    self.assertIsNone(micro_posix_timestamp)


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
    self.assertEqual(len(file_entry._attributes), 0)

    # No extended attributes are returned.
    # Also see: https://github.com/py4n6/pytsk/issues/79.

  def testGetDataStreams(self):
    """Tests the _GetDataStreams function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_streams = file_entry._GetDataStreams()
    self.assertEqual(len(data_streams), 1)

  # TODO: add tests for _GetDirectory
  # TODO: add tests for _GetLink

  def testGetStatAttribute(self):
    """Tests the _GetStatAttribute function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
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

  def testAccessTime(self):
    """Test the access_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.access_time)

  def testBackupTime(self):
    """Test the backup_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.backup_time)

  def testChangeTime(self):
    """Test the change_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.change_time)

  def testCreationTime(self):
    """Test the creation_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.creation_time)

  def testDeletionTime(self):
    """Test the deletion_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.deletion_time)

  def testModificationTime(self):
    """Test the modification_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.modification_time)

  def testName(self):
    """Test the name property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'another_file')

  def testSize(self):
    """Test the size property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 22)

  def testGetExtents(self):
    """Tests the GetExtents function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    extents = file_entry.GetExtents()
    self.assertEqual(len(extents), 1)

    self.assertEqual(extents[0].extent_type, definitions.EXTENT_TYPE_DATA)
    self.assertEqual(extents[0].offset, 527360)
    self.assertEqual(extents[0].size, 1024)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, inode=self._INODE_A_DIRECTORY,
        location='/a_directory', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    extents = file_entry.GetExtents()
    self.assertEqual(len(extents), 0)

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)

  def testGetFileObject(self):
    """Tests the GetFileObject function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    file_object = file_entry.GetFileObject()
    self.assertIsNotNone(file_object)

    self.assertEqual(file_object.get_size(), 22)

    file_object = file_entry.GetFileObject(data_stream_name='bogus')
    self.assertIsNone(file_object)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        location='/a_directory', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    with self.assertRaises(errors.BackEndError):
      file_entry.GetFileObject()

  def testGetLinkedFileEntry(self):
    """Tests the GetLinkedFileEntry function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_LINK,
        location='/a_link', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    linked_file_entry = file_entry.GetLinkedFileEntry()

    self.assertIsNotNone(linked_file_entry)

    self.assertEqual(linked_file_entry.name, 'another_file')

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, 'a_directory')

  # TODO: add tests for GetTSKFile

  def testIsFunctions(self):
    """Tests the Is? functions."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
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

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        location='/a_directory', parent=self._raw_path_spec)
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

    # Note that passwords.txt~ is currently ignored by dfVFS, since
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
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        location='/a_directory', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream = file_entry.GetDataStream('')
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
    self.assertEqual(len(file_entry._attributes), 0)

  def testGetDataStreams(self):
    """Tests the _GetDataStreams function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_streams = file_entry._GetDataStreams()
    self.assertEqual(len(data_streams), 1)

  # TODO: add tests for _GetDirectory
  # TODO: add tests for _GetLink

  def testGetStatAttribute(self):
    """Tests the _GetStatAttribute function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
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

  def testAccessTime(self):
    """Test the access_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.access_time)

  def testBackupTime(self):
    """Test the backup_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.backup_time)

  def testChangeTime(self):
    """Test the change_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.change_time)

  def testCreationTime(self):
    """Test the creation_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.creation_time)

  def testDeletionTime(self):
    """Test the deletion_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.deletion_time)

  def testModificationTime(self):
    """Test the modification_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.modification_time)

  def testName(self):
    """Test the name property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'another_file')

  def testSize(self):
    """Test the size property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 22)

  # TODO: add tests for GetExtents

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)

  def testGetFileObject(self):
    """Tests the GetFileObject function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    file_object = file_entry.GetFileObject()
    self.assertIsNotNone(file_object)

    self.assertEqual(file_object.get_size(), 22)

    file_object = file_entry.GetFileObject(data_stream_name='bogus')
    self.assertIsNone(file_object)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        location='/a_directory', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    with self.assertRaises(errors.BackEndError):
      file_entry.GetFileObject()

  # TODO: add tests for GetLinkedFileEntry

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, 'a_directory')

  # TODO: add tests for GetTSKFile

  def testIsFunctions(self):
    """Tests the Is? functions."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
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

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        location='/a_directory', parent=self._raw_path_spec)
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

    # Note that passwords.txt~ is currently ignored by dfVFS, since
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
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        location='/a_directory', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream = file_entry.GetDataStream('')
    self.assertIsNotNone(data_stream)


class TSKFileEntryTestHFSPlus(shared_test_lib.BaseTestCase):
  """Tests the SleuthKit (TSK) file entry on HFS+."""

  # pylint: disable=protected-access

  _INODE_A_DIRECTORY = 18
  _INODE_A_FILE = 19
  _INODE_A_LINK = 22
  _INODE_ANOTHER_FILE = 21

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
    self.assertEqual(len(file_entry._attributes), 1)

    test_attribute = file_entry._attributes[0]
    self.assertIsInstance(test_attribute, tsk_attribute.TSKExtendedAttribute)
    self.assertEqual(test_attribute.name, 'myxattr')

    test_attribute_value_data = test_attribute.read()
    self.assertEqual(test_attribute_value_data, b'My extended attribute')

  def testGetDataStreams(self):
    """Tests the _GetDataStreams function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_streams = file_entry._GetDataStreams()
    self.assertEqual(len(data_streams), 1)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=25,
        location='/a_directory/a_resourcefork', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_streams = file_entry._GetDataStreams()
    self.assertEqual(len(data_streams), 2)

  # TODO: add tests for _GetDirectory
  # TODO: add tests for _GetLink

  def testGetStatAttribute(self):
    """Tests the _GetStatAttribute function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_attribute = file_entry._GetStatAttribute()

    self.assertIsNotNone(stat_attribute)
    self.assertEqual(stat_attribute.group_identifier, 20)
    self.assertEqual(stat_attribute.inode_number, 21)
    self.assertEqual(stat_attribute.mode, 0o644)
    self.assertEqual(stat_attribute.number_of_links, 1)
    self.assertEqual(stat_attribute.owner_identifier, 501)
    self.assertEqual(stat_attribute.size, 22)
    self.assertEqual(stat_attribute.type, stat_attribute.TYPE_FILE)

  # TODO: add tests for _GetSubFileEntries
  # TODO: add tests for _GetTimeValue

  def testAccessTime(self):
    """Test the access_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.access_time)

  def testBackupTime(self):
    """Test the backup_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.backup_time)

  def testChangeTime(self):
    """Test the change_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.change_time)

  def testCreationTime(self):
    """Test the creation_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.creation_time)

  def testDeletionTime(self):
    """Test the deletion_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.deletion_time)

  def testModificationTime(self):
    """Test the modification_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.modification_time)

  def testName(self):
    """Test the name property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'another_file')

  def testSize(self):
    """Test the size property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 22)

  def testGetExtents(self):
    """Tests the GetExtents function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    extents = file_entry.GetExtents()
    self.assertEqual(len(extents), 1)

    self.assertEqual(extents[0].extent_type, definitions.EXTENT_TYPE_DATA)
    self.assertEqual(extents[0].offset, 1130496)
    self.assertEqual(extents[0].size, 4096)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        location='/a_directory', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    extents = file_entry.GetExtents()
    self.assertEqual(len(extents), 0)

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)

  def testGetFileObject(self):
    """Tests the GetFileObject function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    file_object = file_entry.GetFileObject()
    self.assertIsNotNone(file_object)

    self.assertEqual(file_object.get_size(), 22)

    file_object = file_entry.GetFileObject(data_stream_name='bogus')
    self.assertIsNone(file_object)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        location='/a_directory', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    with self.assertRaises(errors.BackEndError):
      file_entry.GetFileObject()

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=25,
        location='/a_directory/a_resourcefork', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    file_object = file_entry.GetFileObject(data_stream_name='rsrc')
    self.assertIsNotNone(file_object)

    self.assertEqual(file_object.get_size(), 17)

  def testGetLinkedFileEntry(self):
    """Tests the GetLinkedFileEntry function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_LINK,
        location='/a_link', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    linked_file_entry = file_entry.GetLinkedFileEntry()

    self.assertIsNotNone(linked_file_entry)

    self.assertEqual(linked_file_entry.name, 'another_file')

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, 'a_directory')

  # TODO: add tests for GetTSKFile

  def testIsFunctions(self):
    """Tests the Is? functions."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
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

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        location='/a_directory', parent=self._raw_path_spec)
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

    self.assertEqual(file_entry.number_of_sub_file_entries, 3)

  def testDataStreams(self):
    """Tests the data streams functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        location='/a_directory', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=25,
        location='/a_directory/a_resourcefork', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 2)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, ['', 'rsrc'])

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream = file_entry.GetDataStream('')
    self.assertIsNotNone(data_stream)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=25,
        location='/a_directory/a_resourcefork', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream = file_entry.GetDataStream('rsrc')
    self.assertIsNotNone(data_stream)


class TSKFileEntryTestISO9660(shared_test_lib.BaseTestCase):
  """Tests the SleuthKit (TSK) file entry on ISO9660."""

  # pylint: disable=protected-access

  _INODE_A_DIRECTORY = 1
  _INODE_A_FILE = 5
  _INODE_ANOTHER_FILE = 4

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['iso9660.raw'])
    self._SkipIfPathNotExists(test_path)

    self.test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._tsk_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/',
        parent=self.test_os_path_spec)

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
        location='/A_DIRECTORY/A_FILE', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertIsNone(file_entry._attributes)

    file_entry._GetAttributes()
    self.assertIsNotNone(file_entry._attributes)
    self.assertEqual(len(file_entry._attributes), 0)

  def testGetDataStreams(self):
    """Tests the _GetDataStreams function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/A_DIRECTORY/ANOTHER_FILE', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_streams = file_entry._GetDataStreams()
    self.assertEqual(len(data_streams), 1)

  # TODO: add tests for _GetDirectory
  # TODO: add tests for _GetLink

  def testGetStatAttribute(self):
    """Tests the _GetStatAttribute function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/A_DIRECTORY/ANOTHER_FILE', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_attribute = file_entry._GetStatAttribute()

    self.assertIsNotNone(stat_attribute)
    self.assertEqual(stat_attribute.group_identifier, 0)
    self.assertEqual(stat_attribute.inode_number, 4)
    self.assertEqual(stat_attribute.mode, 0)
    self.assertEqual(stat_attribute.number_of_links, 1)
    self.assertEqual(stat_attribute.owner_identifier, 0)
    self.assertEqual(stat_attribute.size, 22)
    self.assertEqual(stat_attribute.type, stat_attribute.TYPE_FILE)

  # TODO: add tests for _GetSubFileEntries
  # TODO: add tests for _GetTimeValue

  def testAccessTime(self):
    """Test the access_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/A_DIRECTORY/ANOTHER_FILE', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.access_time)

  def testBackupTime(self):
    """Test the backup_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/A_DIRECTORY/ANOTHER_FILE', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.backup_time)

  def testChangeTime(self):
    """Test the change_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/A_DIRECTORY/ANOTHER_FILE', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.change_time)

  def testCreationTime(self):
    """Test the creation_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/A_DIRECTORY/ANOTHER_FILE', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.creation_time)

  def testDeletionTime(self):
    """Test the deletion_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/A_DIRECTORY/ANOTHER_FILE', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.deletion_time)

  def testModificationTime(self):
    """Test the modification_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/A_DIRECTORY/ANOTHER_FILE', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.modification_time)

  def testName(self):
    """Test the name property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/A_DIRECTORY/ANOTHER_FILE', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'ANOTHER_FILE')

  def testSize(self):
    """Test the size property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/A_DIRECTORY/ANOTHER_FILE', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 22)

  def testGetExtents(self):
    """Tests the GetExtents function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, inode=self._INODE_ANOTHER_FILE,
        location='/A_DIRECTORY/ANOTHER_FILE', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    extents = file_entry.GetExtents()
    self.assertEqual(len(extents), 1)

    self.assertEqual(extents[0].extent_type, definitions.EXTENT_TYPE_DATA)
    self.assertEqual(extents[0].offset, 55296)
    self.assertEqual(extents[0].size, 2048)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, inode=self._INODE_A_DIRECTORY,
        location='/A_DIRECTORY', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    extents = file_entry.GetExtents()
    self.assertEqual(len(extents), 0)

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)

  def testGetFileObject(self):
    """Tests the GetFileObject function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/A_DIRECTORY/ANOTHER_FILE', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    file_object = file_entry.GetFileObject()
    self.assertIsNotNone(file_object)

    self.assertEqual(file_object.get_size(), 22)

    file_object = file_entry.GetFileObject(data_stream_name='bogus')
    self.assertIsNone(file_object)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        location='/A_DIRECTORY', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    with self.assertRaises(errors.BackEndError):
      file_entry.GetFileObject()

  def testGetLinkedFileEntry(self):
    """Tests the GetLinkedFileEntry function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_FILE,
        location='/A_DIRECTORY/A_FILE', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    linked_file_entry = file_entry.GetLinkedFileEntry()

    self.assertIsNone(linked_file_entry)

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/A_DIRECTORY/ANOTHER_FILE', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, 'A_DIRECTORY')

  # TODO: add tests for GetTSKFile

  def testIsFunctions(self):
    """Tests the Is? functions."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/A_DIRECTORY/ANOTHER_FILE', parent=self.test_os_path_spec)
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

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        location='/A_DIRECTORY', parent=self.test_os_path_spec)
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
        parent=self.test_os_path_spec)
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
        parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 4)

    expected_sub_file_entry_names = [
        'A_DIRECTORY',
        'LOST_FOUND',
        'PASSWORDS.TXT',
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
        parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 2)

  def testDataStreams(self):
    """Tests the data streams functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/A_DIRECTORY/ANOTHER_FILE', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_DIRECTORY,
        location='/A_DIRECTORY', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_ANOTHER_FILE,
        location='/A_DIRECTORY/ANOTHER_FILE', parent=self.test_os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream = file_entry.GetDataStream('')
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
    self.assertEqual(len(file_entry._attributes), 4)

    test_attribute = file_entry._attributes[0]
    self.assertIsInstance(test_attribute, tsk_attribute.TSKAttribute)
    self.assertEqual(
        test_attribute.attribute_type, pytsk3.TSK_FS_ATTR_TYPE_NTFS_SI)

  def testGetDataStreams(self):
    """Tests the _GetDataStreams function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_streams = file_entry._GetDataStreams()
    self.assertEqual(len(data_streams), 1)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=10, location='/$UpCase',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_streams = file_entry._GetDataStreams()
    self.assertEqual(len(data_streams), 2)

  # TODO: add tests for _GetDirectory
  # TODO: add tests for _GetLink

  def testGetStatAttribute(self):
    """Tests the _GetStatAttribute function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
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

    self.assertEqual(file_entry.number_of_attributes, 4)

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
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream = file_entry.GetDataStream('')
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, '')

    data_stream = file_entry.GetDataStream('bogus')
    self.assertIsNone(data_stream)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=10, location='/$UpCase',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream = file_entry.GetDataStream('$Info')
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, '$Info')

  def testGetExtents(self):
    """Tests the GetExtents function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=10, location='/$UpCase',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    extents = file_entry.GetExtents()
    self.assertEqual(len(extents), 1)

    self.assertEqual(extents[0].extent_type, definitions.EXTENT_TYPE_DATA)
    self.assertEqual(extents[0].offset, 823296)
    self.assertEqual(extents[0].size, 131072)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_A_DIRECTORY,
        location='/a_directory', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    extents = file_entry.GetExtents()
    self.assertEqual(len(extents), 0)

  def testGetFileObject(self):
    """Tests the GetFileObject function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=10, location='/$UpCase',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    file_object = file_entry.GetFileObject()
    self.assertIsNotNone(file_object)

    self.assertEqual(file_object.get_size(), 131072)

    file_object = file_entry.GetFileObject(data_stream_name='$Info')
    self.assertIsNotNone(file_object)

    self.assertEqual(file_object.get_size(), 32)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_A_DIRECTORY,
        location='/a_directory', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    with self.assertRaises(errors.BackEndError):
      file_entry.GetFileObject()


if __name__ == '__main__':
  unittest.main()
