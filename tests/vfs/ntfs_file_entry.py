#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using pyfsntfs."""

from __future__ import unicode_literals

import unittest

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import ntfs_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import ntfs_file_entry
from dfvfs.vfs import ntfs_file_system

from tests import test_lib as shared_test_lib


class TestNTFSAttribute(ntfs_file_entry.NTFSAttribute):
  """NTFS attribute for testing."""

  # pylint: disable=abstract-method

  TYPE_INDICATOR = 'test'


class NTFSAttributeTest(shared_test_lib.BaseTestCase):
  """Tests the NTFS attribute."""

  # pylint: disable=protected-access

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    self._ntfs_path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\', parent=self._qcow_path_spec)

    self._file_system = ntfs_file_system.NTFSFileSystem(self._resolver_context)
    self._file_system.Open(self._ntfs_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testIntialize(self):
    """Tests the __init__ function."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=41, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    fsntfs_attribute = file_entry._fsntfs_file_entry.get_attribute(0)
    ntfs_attribute = TestNTFSAttribute(fsntfs_attribute)
    self.assertIsNotNone(ntfs_attribute)

    with self.assertRaises(errors.BackEndError):
      TestNTFSAttribute(None)

  def testAttributeType(self):
    """Test the attribute_type property."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=41, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    fsntfs_attribute = file_entry._fsntfs_file_entry.get_attribute(0)
    ntfs_attribute = TestNTFSAttribute(fsntfs_attribute)

    self.assertEqual(ntfs_attribute.attribute_type, 0x00000010)


class FileNameNTFSAttributeTest(shared_test_lib.BaseTestCase):
  """Tests the NTFS $FILE_NAME attribute."""

  # pylint: disable=protected-access

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    self._ntfs_path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\', parent=self._qcow_path_spec)

    self._file_system = ntfs_file_system.NTFSFileSystem(self._resolver_context)
    self._file_system.Open(self._ntfs_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testIntialize(self):
    """Tests the __init__ function."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=41, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    fsntfs_attribute = file_entry._fsntfs_file_entry.get_attribute(1)
    ntfs_attribute = ntfs_file_entry.FileNameNTFSAttribute(fsntfs_attribute)
    self.assertIsNotNone(ntfs_attribute)

    with self.assertRaises(errors.BackEndError):
      ntfs_file_entry.FileNameNTFSAttribute(None)

  def testAttributeType(self):
    """Test the attribute_type property."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=41, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    fsntfs_attribute = file_entry._fsntfs_file_entry.get_attribute(1)
    ntfs_attribute = ntfs_file_entry.FileNameNTFSAttribute(fsntfs_attribute)

    self.assertEqual(ntfs_attribute.attribute_type, 0x00000030)


# TODO: add tests for ObjectIdentifierNTFSAttribute.
# TODO: add tests for SecurityDescriptorNTFSAttribute.


class StandardInformationNTFSAttributeTest(shared_test_lib.BaseTestCase):
  """Tests the NTFS $STANDARD_INFORMATION attribute."""

  # pylint: disable=protected-access

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    self._ntfs_path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\', parent=self._qcow_path_spec)

    self._file_system = ntfs_file_system.NTFSFileSystem(self._resolver_context)
    self._file_system.Open(self._ntfs_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testIntialize(self):
    """Tests the __init__ function."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=41, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    fsntfs_attribute = file_entry._fsntfs_file_entry.get_attribute(0)
    ntfs_attribute = ntfs_file_entry.StandardInformationNTFSAttribute(
        fsntfs_attribute)
    self.assertIsNotNone(ntfs_attribute)

    with self.assertRaises(errors.BackEndError):
      ntfs_file_entry.StandardInformationNTFSAttribute(None)

  def testAttributeType(self):
    """Test the attribute_type property."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=41, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    fsntfs_attribute = file_entry._fsntfs_file_entry.get_attribute(0)
    ntfs_attribute = ntfs_file_entry.StandardInformationNTFSAttribute(
        fsntfs_attribute)

    self.assertEqual(ntfs_attribute.attribute_type, 0x00000010)


class NTFSDataStream(shared_test_lib.BaseTestCase):
  """Tests the NTFS data stream."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    self._ntfs_path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\', parent=self._qcow_path_spec)

    self._file_system = ntfs_file_system.NTFSFileSystem(self._resolver_context)
    self._file_system.Open(self._ntfs_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testName(self):
    """Test the name property."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=41, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    data_streams = list(file_entry.data_streams)
    self.assertNotEqual(len(data_streams), 0)

    self.assertEqual(data_streams[0].name, '')

  def testIsDefault(self):
    """Test the IsDefault function."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=41, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    data_streams = list(file_entry.data_streams)
    self.assertNotEqual(len(data_streams), 0)

    self.assertTrue(data_streams[0].IsDefault())


class NTFSDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the NTFS directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    self._ntfs_path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\', parent=self._qcow_path_spec)

    self._file_system = ntfs_file_system.NTFSFileSystem(self._resolver_context)
    self._file_system.Open(self._ntfs_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = ntfs_file_entry.NTFSDirectory(
        self._file_system, self._ntfs_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = ntfs_file_entry.NTFSDirectory(
        self._file_system, self._ntfs_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 15)


class NTFSFileEntryTest(shared_test_lib.BaseTestCase):
  """Tests the NTFS file entry."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    self._ntfs_path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\', parent=self._qcow_path_spec)

    self._file_system = ntfs_file_system.NTFSFileSystem(self._resolver_context)
    self._file_system.Open(self._ntfs_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testIntialize(self):
    """Tests the __init__ function."""
    file_entry = ntfs_file_entry.NTFSFileEntry(
        self._resolver_context, self._file_system, self._ntfs_path_spec)

    self.assertIsNotNone(file_entry)

  # TODO: add tests for _GetAttributes
  # TODO: add tests for _GetDataStreams
  # TODO: add tests for _GetDirectory
  # TODO: add tests for _GetLink
  # TODO: add tests for _GetStat
  # TODO: add tests for _GetSubFileEntries
  # TODO: add tests for _IsLink

  def testAccessTime(self):
    """Test the access_time property."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=41, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.access_time)

  def testChangeTime(self):
    """Test the change_time property."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=41, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.change_time)

  def testCreationTime(self):
    """Test the creation_time property."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=41, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.creation_time)

  def testModificationTime(self):
    """Test the modification_time property."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=41, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.modification_time)

  def testName(self):
    """Test the name property."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=41, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'password.txt')

  def testSize(self):
    """Test the size property."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=41, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 116)

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=41, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)

  # TODO: add tests for GetFileObject

  def testGetLinkedFileEntry(self):
    """Tests the GetLinkedFileEntry function."""
    # TODO: need a test image with a link to test.

  # TODO: add tests for GetNTFSFileEntry

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    test_location = (
        '\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_attribute=2, mft_entry=38,
        parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, 'System Volume Information')

  # TODO: add tests for GetSecurityDescriptor

  def testGetStat(self):
    """Tests the GetStat function."""
    test_location = (
        '\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=38, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry.GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.fs_type, 'NTFS')
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 65536)

    self.assertEqual(stat_object.atime, 1386052509)
    self.assertEqual(stat_object.atime_nano, 5023783)
    self.assertEqual(stat_object.ctime, 1386052509)
    self.assertEqual(stat_object.ctime_nano, 5179783)
    self.assertEqual(stat_object.crtime, 1386052509)
    self.assertEqual(stat_object.crtime_nano, 5023783)
    self.assertEqual(stat_object.mtime, 1386052509)
    self.assertEqual(stat_object.mtime_nano, 5179783)

  def testIsAllocated(self):
    """Test the IsAllocated function."""
    test_location = (
        '\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=38, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsAllocated())

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\System Volume Information', mft_entry=36,
        parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsAllocated())

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\', parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsAllocated())

  def testIsDevice(self):
    """Test the IsDevice function."""
    test_location = (
        '\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=38, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsDevice())

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\System Volume Information', mft_entry=36,
        parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsDevice())

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\', parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsDevice())

  def testIsDirectory(self):
    """Test the IsDirectory function."""
    test_location = (
        '\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=38, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsDirectory())

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\System Volume Information', mft_entry=36,
        parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsDirectory())

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\', parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsDirectory())

  def testIsFile(self):
    """Test the IsFile function."""
    test_location = (
        '\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=38, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsFile())

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\System Volume Information', mft_entry=36,
        parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsFile())

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\', parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsFile())

  def testIsLink(self):
    """Test the IsLink function."""
    test_location = (
        '\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=38, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsLink())

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\System Volume Information', mft_entry=36,
        parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsLink())

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\', parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsLink())

  def testIsPipe(self):
    """Test the IsPipe function."""
    test_location = (
        '\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=38, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsPipe())

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\System Volume Information', mft_entry=36,
        parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsPipe())

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\', parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsPipe())

  def testIsRoot(self):
    """Test the IsRoot function."""
    test_location = (
        '\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=38, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsRoot())

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\System Volume Information', mft_entry=36,
        parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsRoot())

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\', parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsRoot())

  def testIsSocket(self):
    """Test the IsSocket functions."""
    test_location = (
        '\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=38, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsSocket())

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\System Volume Information', mft_entry=36,
        parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsSocket())

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\', parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsSocket())

  def testIsVirtual(self):
    """Test the IsVirtual functions."""
    test_location = (
        '\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=38, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsVirtual())

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\System Volume Information', mft_entry=36,
        parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsVirtual())

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\', parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertFalse(file_entry.IsVirtual())

  def testSubFileEntries(self):
    """Test the sub file entries properties."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\', parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 15)

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
        'another_file',
        'password.txt',
        'syslog.gz',
        'System Volume Information']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))

    # Test a path specification without a location.
    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=36, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 3)

  def testAttributes(self):
    """Test the attributes properties."""
    test_location = (
        '\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
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

    stat_time, stat_time_nano = (
        attribute.modification_time.CopyToStatTimeTuple())
    self.assertEqual(stat_time, 1386052509)
    self.assertEqual(stat_time_nano, 5179783)

    attribute = attributes[1]

    self.assertEqual(
        attribute.type_indicator, definitions.ATTRIBUTE_TYPE_NTFS_FILE_NAME)

    self.assertIsNotNone(attribute.access_time)
    self.assertIsNotNone(attribute.creation_time)
    self.assertIsNotNone(attribute.modification_time)
    self.assertIsNotNone(attribute.entry_modification_time)

    stat_time, stat_time_nano = attribute.access_time.CopyToStatTimeTuple()
    self.assertEqual(stat_time, 1386052509)
    self.assertEqual(stat_time_nano, 5023783)

    attribute = attributes[2]

    self.assertEqual(
        attribute.type_indicator, definitions.ATTRIBUTE_TYPE_NTFS_FILE_NAME)

    # Tests a file entry with the $SECURITY_DESCRIPTOR attribute.
    test_location = '\\$AttrDef'
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=4, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_attributes, 4)

    attributes = list(file_entry.attributes)

    attribute = attributes[2]

    self.assertEqual(
        attribute.type_indicator,
        definitions.ATTRIBUTE_TYPE_NTFS_SECURITY_DESCRIPTOR)

    security_descriptor = attribute.security_descriptor
    self.assertIsNotNone(security_descriptor)

    security_identifier = security_descriptor.owner
    self.assertIsNotNone(security_identifier)
    expected_string = 'S-1-5-21-4060289323-199701022-3924801681-1000'
    self.assertEqual(security_identifier.string, expected_string)

    security_identifier = security_descriptor.group
    self.assertIsNotNone(security_identifier)
    self.assertEqual(security_identifier.string, 'S-1-5-32-544')

    access_control_list = security_descriptor.discretionary_acl
    self.assertIsNone(access_control_list)

    access_control_list = security_descriptor.system_acl
    self.assertIsNotNone(access_control_list)
    self.assertEqual(access_control_list.number_of_entries, 2)

    access_control_entry = access_control_list.get_entry(0)
    self.assertIsNotNone(access_control_entry)

    self.assertEqual(access_control_entry.type, 0)
    self.assertEqual(access_control_entry.flags, 0)
    self.assertEqual(access_control_entry.access_mask, 0x120089)

    security_identifier = access_control_entry.security_identifier
    self.assertIsNotNone(security_identifier)
    self.assertEqual(security_identifier.string, 'S-1-5-18')

  def testDataStream(self):
    """Tests the data streams properties."""
    test_location = (
        '\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=38, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\System Volume Information', mft_entry=36,
        parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

    test_location = '\\$Extend\\$RmMetadata\\$Repair'
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=28, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 2)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(sorted(data_stream_names), sorted(['', '$Config']))

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    test_location = (
        '\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=38, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = ''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, data_stream_name)

    data_stream = file_entry.GetDataStream('bogus')
    self.assertIsNone(data_stream)

    test_location = '\\$Extend\\$RmMetadata\\$Repair'
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=28, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = '$Config'
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, data_stream_name)

  def testGetSecurityDescriptor(self):
    """Tests the GetSecurityDescriptor function."""
    # pylint: disable=no-member

    test_location = (
        '\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=38, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    security_descriptor = file_entry.GetSecurityDescriptor()
    self.assertIsNotNone(security_descriptor)

    security_identifier = security_descriptor.owner
    self.assertIsNotNone(security_identifier)
    self.assertEqual(security_identifier.string, 'S-1-5-32-544')

    security_identifier = security_descriptor.group
    self.assertIsNotNone(security_identifier)
    self.assertEqual(security_identifier.string, 'S-1-5-18')

    access_control_list = security_descriptor.discretionary_acl
    self.assertIsNone(access_control_list)

    access_control_list = security_descriptor.system_acl
    self.assertIsNotNone(access_control_list)
    self.assertEqual(access_control_list.number_of_entries, 1)

    access_control_entry = access_control_list.get_entry(0)
    self.assertIsNotNone(access_control_entry)

    self.assertEqual(access_control_entry.type, 0)
    self.assertEqual(access_control_entry.flags, 0)
    self.assertEqual(access_control_entry.access_mask, 0x10000)

    security_identifier = access_control_entry.security_identifier
    self.assertIsNotNone(security_identifier)
    self.assertEqual(security_identifier.string, 'S-1-5-32-544')

    # Tests a file entry with the $SECURITY_DESCRIPTOR attribute.
    test_location = '\\$AttrDef'
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=test_location, mft_entry=4, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    security_descriptor = file_entry.GetSecurityDescriptor()
    self.assertIsNotNone(security_descriptor)

    security_identifier = security_descriptor.owner
    self.assertIsNotNone(security_identifier)
    expected_string = 'S-1-5-21-4060289323-199701022-3924801681-1000'
    self.assertEqual(security_identifier.string, expected_string)

    security_identifier = security_descriptor.group
    self.assertIsNotNone(security_identifier)
    self.assertEqual(security_identifier.string, 'S-1-5-32-544')

    access_control_list = security_descriptor.discretionary_acl
    self.assertIsNone(access_control_list)

    access_control_list = security_descriptor.system_acl
    self.assertIsNotNone(access_control_list)
    self.assertEqual(access_control_list.number_of_entries, 2)

    access_control_entry = access_control_list.get_entry(0)
    self.assertIsNotNone(access_control_entry)

    self.assertEqual(access_control_entry.type, 0)
    self.assertEqual(access_control_entry.flags, 0)
    self.assertEqual(access_control_entry.access_mask, 0x120089)

    security_identifier = access_control_entry.security_identifier
    self.assertIsNotNone(security_identifier)
    self.assertEqual(security_identifier.string, 'S-1-5-18')


if __name__ == '__main__':
  unittest.main()
