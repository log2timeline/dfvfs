#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using pyfsntfs."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import ntfs_file_entry
from dfvfs.vfs import ntfs_file_system

from tests import test_lib as shared_test_lib


class NTFSFileEntryTest(shared_test_lib.BaseTestCase):
  """Tests the NTFS file entry."""

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
    self._ntfs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\',
        parent=self._raw_path_spec)

    self._file_system = ntfs_file_system.NTFSFileSystem(
        self._resolver_context, self._ntfs_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testIntialize(self):
    """Tests the __init__ function."""
    file_entry = ntfs_file_entry.NTFSFileEntry(
        self._resolver_context, self._file_system, self._ntfs_path_spec)

    self.assertIsNotNone(file_entry)

  # TODO: add tests for _GetAttributes

  def testGetDataStreams(self):
    """Tests the _GetDataStreams function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory\\another_file',
        mft_entry=self._MFT_ENTRY_ANOTHER_FILE, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_streams = file_entry._GetDataStreams()
    self.assertEqual(len(data_streams), 1)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\$UpCase', mft_entry=10,
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
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory\\a_file',
        mft_entry=self._MFT_ENTRY_A_FILE, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_attribute = file_entry._GetStatAttribute()

    self.assertIsNotNone(stat_attribute)
    self.assertEqual(stat_attribute.inode_number, 0x1000000000041)
    # TODO: requires changes to pyfsntfs
    self.assertIsNone(stat_attribute.number_of_links)
    self.assertEqual(stat_attribute.size, 53)
    self.assertEqual(stat_attribute.type, stat_attribute.TYPE_FILE)

  # TODO: add tests for _GetSubFileEntries
  # TODO: add tests for _IsLink

  def testAccessTime(self):
    """Test the access_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, mft_attribute=1,
        mft_entry=self._MFT_ENTRY_PASSWORDS_TXT, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.access_time)

  def testAttributes(self):
    """Test the attributes properties."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory\\a_file',
        mft_entry=self._MFT_ENTRY_A_FILE, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_attributes, 4)

    attributes = list(file_entry.attributes)
    attribute = attributes[0]

    self.assertEqual(
        attribute.type_indicator,
        definitions.ATTRIBUTE_TYPE_NTFS_STANDARD_INFORMATION)

    self.assertIsNotNone(attribute.access_time)
    self.assertIsNotNone(attribute.creation_time)
    self.assertIsNotNone(attribute.modification_time)
    self.assertIsNotNone(attribute.entry_modification_time)

    date_time_string = (
        attribute.modification_time.CopyToDateTimeStringISO8601())
    self.assertEqual(date_time_string, '2019-08-31T10:22:59.9581788+00:00')

    attribute = attributes[1]

    self.assertEqual(
        attribute.type_indicator, definitions.ATTRIBUTE_TYPE_NTFS_FILE_NAME)

    self.assertIsNotNone(attribute.access_time)
    self.assertIsNotNone(attribute.creation_time)
    self.assertIsNotNone(attribute.modification_time)
    self.assertIsNotNone(attribute.entry_modification_time)

    date_time_string = (
        attribute.access_time.CopyToDateTimeStringISO8601())
    self.assertEqual(date_time_string, '2019-08-31T10:22:59.9567496+00:00')

    attribute = attributes[2]

    self.assertEqual(
        attribute.type_indicator,
        definitions.ATTRIBUTE_TYPE_NTFS_SECURITY_DESCRIPTOR)

    security_descriptor = attribute.security_descriptor
    self.assertIsNotNone(security_descriptor)

    security_identifier = security_descriptor.owner
    self.assertIsNotNone(security_identifier)
    self.assertEqual(security_identifier.string, 'S-1-5-32-544')

    security_identifier = security_descriptor.group
    self.assertIsNotNone(security_identifier)
    self.assertEqual(security_identifier.string, 'S-1-5-32-544')

    access_control_list = security_descriptor.system_acl
    self.assertIsNone(access_control_list)

    access_control_list = security_descriptor.discretionary_acl
    self.assertIsNotNone(access_control_list)
    self.assertEqual(access_control_list.number_of_entries, 1)

    access_control_entry = access_control_list.get_entry(0)
    self.assertIsNotNone(access_control_entry)

    self.assertEqual(access_control_entry.type, 0)
    self.assertEqual(access_control_entry.flags, 3)
    self.assertEqual(access_control_entry.access_mask, 0x1f01ff)

    security_identifier = access_control_entry.security_identifier
    self.assertIsNotNone(security_identifier)
    self.assertEqual(security_identifier.string, 'S-1-1-0')

  def testChangeTime(self):
    """Test the change_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, mft_attribute=1,
        mft_entry=self._MFT_ENTRY_PASSWORDS_TXT, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.change_time)

  def testCreationTime(self):
    """Test the creation_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, mft_attribute=1,
        mft_entry=self._MFT_ENTRY_PASSWORDS_TXT, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.creation_time)

  def testDataStream(self):
    """Tests the data streams properties."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory\\a_file',
        mft_entry=self._MFT_ENTRY_A_FILE, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory',
        mft_entry=self._MFT_ENTRY_A_DIRECTORY, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\$UpCase', mft_entry=10,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 2)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    expected_data_stream_names = sorted(['', '$Info'])
    self.assertEqual(sorted(data_stream_names), expected_data_stream_names)

  def testModificationTime(self):
    """Test the modification_time property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, mft_attribute=1,
        mft_entry=self._MFT_ENTRY_PASSWORDS_TXT, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.modification_time)

  def testName(self):
    """Test the name property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, mft_attribute=1,
        mft_entry=self._MFT_ENTRY_PASSWORDS_TXT, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'passwords.txt')

  def testSize(self):
    """Test the size property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, mft_attribute=1,
        mft_entry=self._MFT_ENTRY_PASSWORDS_TXT, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 116)

  def testSubFileEntries(self):
    """Test the sub file entries properties."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 14)

    expected_sub_file_entry_names = [
        '$AttrDef',
        '$BadClus',
        '$Bitmap',
        '$Boot',
        '$Extend',
        '$LogFile',
        '$MFT',
        '$MFTMirr',
        '$Secure',
        '$UpCase',
        '$Volume',
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
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, mft_attribute=1,
        mft_entry=self._MFT_ENTRY_A_DIRECTORY, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 2)

  def testGetExtents(self):
    """Tests the GetExtents function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\$UpCase', mft_entry=10,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    extents = file_entry.GetExtents()
    self.assertEqual(len(extents), 1)

    self.assertEqual(extents[0].extent_type, definitions.EXTENT_TYPE_DATA)
    self.assertEqual(extents[0].offset, 823296)
    self.assertEqual(extents[0].size, 131072)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory',
        mft_entry=self._MFT_ENTRY_A_DIRECTORY, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    extents = file_entry.GetExtents()
    self.assertEqual(len(extents), 0)

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, mft_attribute=1,
        mft_entry=self._MFT_ENTRY_PASSWORDS_TXT, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)

  def testGetFileObject(self):
    """Tests the GetFileObject function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\$UpCase', mft_entry=10,
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
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory',
        mft_entry=self._MFT_ENTRY_A_DIRECTORY, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    file_object = file_entry.GetFileObject()
    self.assertIsNone(file_object)

  def testGetLinkedFileEntry(self):
    """Tests the GetLinkedFileEntry function."""
    # TODO: need a test image with a link to test.

  # TODO: add tests for GetNTFSFileEntry

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory\\a_file',
        mft_entry=self._MFT_ENTRY_A_FILE, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, 'a_directory')

  # TODO: add tests for GetSecurityDescriptor

  def testIsAllocated(self):
    """Test the IsAllocated function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory\\a_file',
        mft_entry=self._MFT_ENTRY_A_FILE, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsAllocated())

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory',
        mft_entry=self._MFT_ENTRY_A_DIRECTORY, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsAllocated())

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsAllocated())

  def testIsDevice(self):
    """Test the IsDevice function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory\\a_file',
        mft_entry=self._MFT_ENTRY_A_FILE, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsDevice())

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory',
        mft_entry=self._MFT_ENTRY_A_DIRECTORY, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsDevice())

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsDevice())

  def testIsDirectory(self):
    """Test the IsDirectory function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory\\a_file',
        mft_entry=self._MFT_ENTRY_A_FILE, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsDirectory())

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory',
        mft_entry=self._MFT_ENTRY_A_DIRECTORY, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsDirectory())

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsDirectory())

  def testIsFile(self):
    """Test the IsFile function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory\\a_file',
        mft_entry=self._MFT_ENTRY_A_FILE, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsFile())

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory',
        mft_entry=self._MFT_ENTRY_A_DIRECTORY, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsFile())

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsFile())

  def testIsLink(self):
    """Test the IsLink function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory\\a_file',
        mft_entry=self._MFT_ENTRY_A_FILE, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsLink())

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory',
        mft_entry=self._MFT_ENTRY_A_DIRECTORY, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsLink())

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsLink())

  def testIsPipe(self):
    """Test the IsPipe function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory\\a_file',
        mft_entry=self._MFT_ENTRY_A_FILE, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsPipe())

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory',
        mft_entry=self._MFT_ENTRY_A_DIRECTORY, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsPipe())

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsPipe())

  def testIsRoot(self):
    """Test the IsRoot function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory\\a_file',
        mft_entry=self._MFT_ENTRY_A_FILE, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsRoot())

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory',
        mft_entry=self._MFT_ENTRY_A_DIRECTORY, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsRoot())

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsRoot())

  def testIsSocket(self):
    """Test the IsSocket functions."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory\\a_file',
        mft_entry=self._MFT_ENTRY_A_FILE, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsSocket())

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory',
        mft_entry=self._MFT_ENTRY_A_DIRECTORY, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsSocket())

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsSocket())

  def testIsVirtual(self):
    """Test the IsVirtual functions."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory\\a_file',
        mft_entry=self._MFT_ENTRY_A_FILE, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsVirtual())

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory',
        mft_entry=self._MFT_ENTRY_A_DIRECTORY, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsVirtual())

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsVirtual())

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory\\another_file',
        mft_entry=self._MFT_ENTRY_ANOTHER_FILE, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream = file_entry.GetDataStream('')
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, '')

    data_stream = file_entry.GetDataStream('bogus')
    self.assertIsNone(data_stream)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\$UpCase', mft_entry=10,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream = file_entry.GetDataStream('$Info')
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, '$Info')

  def testGetSecurityDescriptor(self):
    """Tests the GetSecurityDescriptor function."""
    # pylint: disable=no-member

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory\\a_file',
        mft_entry=self._MFT_ENTRY_A_FILE, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    security_descriptor = file_entry.GetSecurityDescriptor()
    self.assertIsNotNone(security_descriptor)

    security_identifier = security_descriptor.owner
    self.assertIsNotNone(security_identifier)
    self.assertEqual(security_identifier.string, 'S-1-5-32-544')

    security_identifier = security_descriptor.group
    self.assertIsNotNone(security_identifier)
    self.assertEqual(security_identifier.string, 'S-1-5-32-544')

    access_control_list = security_descriptor.system_acl
    self.assertIsNone(access_control_list)

    access_control_list = security_descriptor.discretionary_acl
    self.assertIsNotNone(access_control_list)
    self.assertEqual(access_control_list.number_of_entries, 1)

    access_control_entry = access_control_list.get_entry(0)
    self.assertIsNotNone(access_control_entry)

    self.assertEqual(access_control_entry.type, 0)
    self.assertEqual(access_control_entry.flags, 3)
    self.assertEqual(access_control_entry.access_mask, 0x1f01ff)

    security_identifier = access_control_entry.security_identifier
    self.assertIsNotNone(security_identifier)
    self.assertEqual(security_identifier.string, 'S-1-1-0')


if __name__ == '__main__':
  unittest.main()
