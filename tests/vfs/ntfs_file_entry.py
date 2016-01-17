#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using the pyfsntfs."""

import os
import unittest

from dfvfs.lib import definitions
from dfvfs.path import ntfs_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import ntfs_file_entry
from dfvfs.vfs import ntfs_file_system


class NTFSFileEntryTest(unittest.TestCase):
  """The unit test for the NTFS file entry object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'vsstest.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    self._ntfs_path_spec = ntfs_path_spec.NTFSPathSpec(
        location=u'\\', parent=self._qcow_path_spec)

    self._file_system = ntfs_file_system.NTFSFileSystem(self._resolver_context)
    self._file_system.Open(self._ntfs_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()

  def testIntialize(self):
    """Test the initialize functionality."""
    file_entry = ntfs_file_entry.NTFSFileEntry(
        self._resolver_context, self._file_system, self._ntfs_path_spec)

    self.assertIsNotNone(file_entry)

  def testGetFileEntryByPathSpec(self):
    """Test the get entry by path specification functionality."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=41, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)

  def testGetLinkedFileEntry(self):
    """Test the get linked file entry functionality."""
    # TODO: need a test image with a link to test.

  def testGetParentFileEntry(self):
    """Test the get parent file entry functionality."""
    test_location = (
        u'\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_attribute=2, mft_entry=38,
        parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, u'System Volume Information')

  def testGetStat(self):
    """Test the get stat functionality."""
    test_location = (
        u'\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=38, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry.GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 65536)

  def testIsFunctions(self):
    """Test the Is? functionality."""
    test_location = (
        u'\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=38, parent=self._qcow_path_spec)
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

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=u'\\System Volume Information', mft_entry=36,
        parent=self._qcow_path_spec)
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

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=u'\\', parent=self._qcow_path_spec)
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
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=u'\\', parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 15)

    expected_sub_file_entry_names = [
        u'$AttrDef',
        u'$BadClus',
        u'$Bitmap',
        u'$Boot',
        u'$Extend',
        u'$LogFile',
        u'$MFT',
        u'$MFTMirr',
        u'$Secure',
        u'$UpCase',
        u'$Volume',
        u'another_file',
        u'password.txt',
        u'syslog.gz',
        u'System Volume Information']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))

  def testAttributes(self):
    """Test the attributes functionality."""
    test_location = (
        u'\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=38, parent=self._qcow_path_spec)
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

    stat_time, stat_time_nano = attribute.modification_time.CopyToStatObject()
    self.assertEqual(stat_time, 1386052509)
    self.assertEqual(stat_time_nano, 5179783)

    attribute = attributes[1]

    self.assertEqual(
        attribute.type_indicator, definitions.ATTRIBUTE_TYPE_NTFS_FILE_NAME)

    self.assertIsNotNone(attribute.access_time)
    self.assertIsNotNone(attribute.creation_time)
    self.assertIsNotNone(attribute.modification_time)
    self.assertIsNotNone(attribute.entry_modification_time)

    stat_time, stat_time_nano = attribute.access_time.CopyToStatObject()
    self.assertEqual(stat_time, 1386052509)
    self.assertEqual(stat_time_nano, 5023783)

    attribute = attributes[2]

    self.assertEqual(
        attribute.type_indicator, definitions.ATTRIBUTE_TYPE_NTFS_FILE_NAME)

  def testDataStream(self):
    """Test the data streams functionality."""
    test_location = (
        u'\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=38, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [u''])

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=u'\\System Volume Information', mft_entry=36,
        parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

    test_location = u'\\$Extend\\$RmMetadata\\$Repair'
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=28, parent=self._qcow_path_spec)
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
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=38, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = u''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, data_stream_name)

    data_stream = file_entry.GetDataStream(u'bogus')
    self.assertIsNone(data_stream)

    test_location = u'\\$Extend\\$RmMetadata\\$Repair'
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=28, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = u'$Config'
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, data_stream_name)


if __name__ == '__main__':
  unittest.main()
