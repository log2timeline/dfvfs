#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the VFS file entry interface."""

from __future__ import unicode_literals

import unittest

from dfvfs.lib import errors
from dfvfs.path import fake_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import fake_file_system
from dfvfs.vfs import file_entry

from tests import test_lib as shared_test_lib


class TestFileEntry(file_entry.FileEntry):
  """File entry for testing."""

  # pylint: disable=abstract-method

  TYPE_INDICATOR = 'test'

  def _GetDirectory(self):
    """Retrieves the directory.

    Returns:
      Directory: a directory or None.
    """
    return file_entry.Directory(self._file_system, self.path_spec)

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Returns:
      generator[FileEntry]: a sub file entry generator.
    """
    return iter([])


class AttributeTest(shared_test_lib.BaseTestCase):
  """Tests the VFS attribute interface."""

  def testTypeIndicator(self):
    """Tests the type_indicator property."""
    attribute = file_entry.Attribute()
    self.assertIsNone(attribute.type_indicator)


class DataStreamTest(shared_test_lib.BaseTestCase):
  """Tests the VFS data stream interface."""

  def testName(self):
    """Test the name property."""
    test_data_stream = file_entry.DataStream()
    self.assertEqual(test_data_stream.name, '')

  def testIsDefault(self):
    """Test the IsDefault function."""
    test_data_stream = file_entry.DataStream()
    self.assertTrue(test_data_stream.IsDefault())


class DirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the VFS directory interface."""

  # pylint: disable=protected-access

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    self._path_spec = fake_path_spec.FakePathSpec(location='/')

    self._file_system = fake_file_system.FakeFileSystem(self._resolver_context)
    self._file_system.Open(self._path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    test_directory = file_entry.Directory(self._file_system, self._path_spec)

    generator = test_directory._EntriesGenerator()
    self.assertIsNotNone(generator)

  def testEntries(self):
    """Tests the entries property."""
    test_directory = file_entry.Directory(self._file_system, self._path_spec)

    self.assertEqual(list(test_directory.entries), [])


class FileEntryTest(shared_test_lib.BaseTestCase):
  """Tests the VFS file entry interface."""

  # pylint: disable=protected-access

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    self._path_spec = fake_path_spec.FakePathSpec(location='/')

    self._file_system = fake_file_system.FakeFileSystem(self._resolver_context)
    self._file_system.Open(self._path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testIntialize(self):
    """Tests the __init__ function."""
    with self.assertRaises(ValueError):
      file_entry.FileEntry(
          self._resolver_context, self._file_system, self._path_spec)

  def testGetAttributes(self):
    """Tests the _GetAttributes function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    attributes = test_file_entry._GetAttributes()
    self.assertEqual(attributes, [])

  def testGetDataStreams(self):
    """Tests the _GetDataStreams function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    data_streams = test_file_entry._GetDataStreams()
    self.assertEqual(data_streams, [])

  def testGetLink(self):
    """Tests the _GetLink function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    symbolic_link = test_file_entry._GetLink()
    self.assertIsNotNone(symbolic_link)

  def testGetStatProtected(self):
    """Tests the _GetStat function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    stat_object = test_file_entry._GetStat()
    self.assertIsNotNone(stat_object)

  def testAccessTime(self):
    """Tests the access_time property."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertIsNone(test_file_entry.access_time)

  def testAddedTime(self):
    """Tests the added_time property."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertIsNone(test_file_entry.added_time)

  def testAttributes(self):
    """Tests the attributes property."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertEqual(test_file_entry.attributes, [])

  def testBackupTime(self):
    """Tests the backup_time property."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertIsNone(test_file_entry.backup_time)

  def testChangeTime(self):
    """Tests the change_time property."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertIsNone(test_file_entry.change_time)

  def testCreationTime(self):
    """Tests the creation_time property."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertIsNone(test_file_entry.creation_time)

  def testDeletionTime(self):
    """Tests the deletion_time property."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertIsNone(test_file_entry.deletion_time)

  def testDataStreams(self):
    """Tests the data_streams property."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertEqual(test_file_entry.data_streams, [])

  def testLink(self):
    """Tests the link property."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertIsNone(test_file_entry.link)

  def testModificationTime(self):
    """Tests the modification_time property."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertIsNone(test_file_entry.modification_time)

  def testName(self):
    """Tests the name property."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertIsNone(test_file_entry.name)

  def testNumberOfAttributes(self):
    """Tests the number_of_attributes property."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertEqual(test_file_entry.number_of_attributes, 0)

  def testNumberOfDataStreams(self):
    """Tests the number_of_data_streams property."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertEqual(test_file_entry.number_of_data_streams, 0)

  def testNumberOfSubFileEntries(self):
    """Tests the number_of_sub_file_entries property."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertEqual(test_file_entry.number_of_sub_file_entries, 0)

  def testSubFileEntries(self):
    """Tests the sub_file_entries property."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertIsNotNone(test_file_entry.sub_file_entries)

  def testTypeIndicator(self):
    """Tests the type_indicator property."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertEqual(test_file_entry.type_indicator, 'test')

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    data_stream = test_file_entry.GetDataStream('')
    self.assertIsNone(data_stream)

    with self.assertRaises(ValueError):
      test_file_entry.GetDataStream(0)

  def testGetFileObject(self):
    """Tests the GetFileObject function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    file_object = test_file_entry.GetFileObject('bogus')
    self.assertIsNone(file_object)

    with self.assertRaises(errors.NotSupported):
      test_file_entry.GetFileObject('')

  def testGetFileSystem(self):
    """Tests the GetFileSystem function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    file_system = test_file_entry.GetFileSystem()
    self.assertIsNotNone(file_system)

  def testGetLinkedFileEntry(self):
    """Tests the GetLinkedFileEntry function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    linked_file_entry = test_file_entry.GetLinkedFileEntry()
    self.assertIsNone(linked_file_entry)

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    parent_file_entry = test_file_entry.GetParentFileEntry()
    self.assertIsNone(parent_file_entry)

  def testGetSubFileEntryByName(self):
    """Tests the GetSubFileEntryByName function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    sub_file_entry = test_file_entry.GetSubFileEntryByName('bogus')
    self.assertIsNone(sub_file_entry)

  def testGetStat(self):
    """Tests the GetStat function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    stat_object = test_file_entry.GetStat()
    self.assertIsNotNone(stat_object)

  def testHasDataStream(self):
    """Tests the HasDataStream function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertFalse(test_file_entry.HasDataStream(''))

    with self.assertRaises(ValueError):
      test_file_entry.HasDataStream(0)

  def testHasExternalData(self):
    """Tests the HasExternalData function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertFalse(test_file_entry.HasExternalData())

  def testIsAllocated(self):
    """Tests the IsAllocated function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertTrue(test_file_entry.IsAllocated())

  def testIsDevice(self):
    """Tests the IsDevice function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertFalse(test_file_entry.IsDevice())

  def testIsDirectory(self):
    """Tests the IsDirectory function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertFalse(test_file_entry.IsDirectory())

  def testIsFile(self):
    """Tests the IsFile function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertFalse(test_file_entry.IsFile())

  def testIsLink(self):
    """Tests the IsLink function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertFalse(test_file_entry.IsLink())

  def testIsPipe(self):
    """Tests the IsPipe function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertFalse(test_file_entry.IsPipe())

  def testIsRoot(self):
    """Tests the IsRoot function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertFalse(test_file_entry.IsRoot())

  def testIsSocket(self):
    """Tests the IsSocket function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertFalse(test_file_entry.IsSocket())

  def testIsVirtual(self):
    """Tests the IsVirtual function."""
    test_file_entry = TestFileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertFalse(test_file_entry.IsVirtual())


if __name__ == '__main__':
  unittest.main()
