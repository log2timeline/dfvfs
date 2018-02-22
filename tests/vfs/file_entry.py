#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the VFS file entry interface."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import fake_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import fake_file_system
from dfvfs.vfs import file_entry

from tests import test_lib as shared_test_lib


class AttributeTest(shared_test_lib.BaseTestCase):
  """Tests the VFS attribute interface."""

  def testTypeIndicator(self):
    """Test the type_indicator property."""
    test_attribute = file_entry.Attribute()

    with self.assertRaises(NotImplementedError):
      _ = test_attribute.type_indicator


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

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    self._fake_path_spec = fake_path_spec.FakePathSpec(location='/')

  # TODO: add tests for _EntriesGenerator function.

  def testEntries(self):
    """Test the entries property."""
    file_system = fake_file_system.FakeFileSystem(self._resolver_context)
    file_system.Open(self._fake_path_spec)

    test_directory = file_entry.Directory(file_system, self._fake_path_spec)
    self.assertEqual(list(test_directory.entries), [])

    file_system.Close()


class FileEntryTest(shared_test_lib.BaseTestCase):
  """Tests the VFS file entry interface."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    self._path_spec = fake_path_spec.FakePathSpec(location='/')

    self._file_system = fake_file_system.FakeFileSystem(self._resolver_context)
    self._file_system.Open(self._path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()

  def testIntialize(self):
    """Test the __init__ function."""
    test_file_entry = file_entry.FileEntry(
        self._resolver_context, self._file_system, self._path_spec)

    self.assertIsNotNone(test_file_entry)

  # TODO: add tests for _GetAttributes function.
  # TODO: add tests for _GetDataStreams function.
  # TODO: add tests for _GetDirectory function.
  # TODO: add tests for _GetLink function.
  # TODO: add tests for _GetStat function.

  def testAccessTime(self):
    """Test the access_time property."""
    test_file_entry = file_entry.FileEntry(
        self._resolver_context, self._file_system, self._path_spec)
    self.assertIsNone(test_file_entry.access_time)

  # TODO: add tests for attributes property.

  def testChangeTime(self):
    """Test the change_time property."""
    test_file_entry = file_entry.FileEntry(
        self._resolver_context, self._file_system, self._path_spec)
    self.assertIsNone(test_file_entry.change_time)

  def testCreationTime(self):
    """Test the creation_time property."""
    test_file_entry = file_entry.FileEntry(
        self._resolver_context, self._file_system, self._path_spec)
    self.assertIsNone(test_file_entry.creation_time)

  # TODO: add tests for data_streams property.
  # TODO: add tests for link property.

  def testModificationTime(self):
    """Test the modification_time property."""
    test_file_entry = file_entry.FileEntry(
        self._resolver_context, self._file_system, self._path_spec)
    self.assertIsNone(test_file_entry.modification_time)

  # TODO: add tests for name property.
  # TODO: add tests for number_of_attributes property.
  # TODO: add tests for number_of_data_streams property.
  # TODO: add tests for number_of_sub_file_entries property.
  # TODO: add tests for sub_file_entries property.
  # TODO: add tests for type_indicator property.
  # TODO: add tests for GetDataStream function.
  # TODO: add tests for GetFileObject function.
  # TODO: add tests for GetFileSystem function.
  # TODO: add tests for GetLinkedFileEntry function.
  # TODO: add tests for GetParentFileEntry function.
  # TODO: add tests for GetSubFileEntryByName function.
  # TODO: add tests for GetStat function.
  # TODO: add tests for HasDataStream function.
  # TODO: add tests for HasExternalData function.
  # TODO: add tests for IsAllocated function.
  # TODO: add tests for IsDevice function.
  # TODO: add tests for IsDirectory function.
  # TODO: add tests for IsFile function.
  # TODO: add tests for IsLink function.
  # TODO: add tests for IsPipe function.
  # TODO: add tests for IsRoot function.
  # TODO: add tests for IsSocket function.
  # TODO: add tests for IsVirtual function.


if __name__ == '__main__':
  unittest.main()
