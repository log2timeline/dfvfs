#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the data stream implementation using pyfsntfs."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import ntfs_data_stream
from dfvfs.vfs import ntfs_file_system

from tests import test_lib as shared_test_lib


class NTFSDataStreamTest(shared_test_lib.BaseTestCase):
  """Tests the NTFS data stream."""

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

  def testName(self):
    """Test the name property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\$UpCase', mft_entry=10,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    test_data_stream = ntfs_data_stream.NTFSDataStream(file_entry, None)
    self.assertEqual(test_data_stream.name, '')

    fsntfs_file_entry = file_entry.GetNTFSFileEntry()
    self.assertIsNotNone(fsntfs_file_entry)

    fsntfs_data_stream = fsntfs_file_entry.get_alternate_data_stream_by_name(
        '$Info')

    test_data_stream = ntfs_data_stream.NTFSDataStream(
        file_entry, fsntfs_data_stream)
    self.assertEqual(test_data_stream.name, '$Info')

  def testGetExtents(self):
    """Test the GetExtents function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\$UpCase', mft_entry=10,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    test_data_stream = ntfs_data_stream.NTFSDataStream(file_entry, None)

    extents = test_data_stream.GetExtents()
    self.assertEqual(len(extents), 1)

    self.assertEqual(extents[0].extent_type, definitions.EXTENT_TYPE_DATA)
    self.assertEqual(extents[0].offset, 823296)
    self.assertEqual(extents[0].size, 131072)

    fsntfs_file_entry = file_entry.GetNTFSFileEntry()
    self.assertIsNotNone(fsntfs_file_entry)

    fsntfs_data_stream = fsntfs_file_entry.get_alternate_data_stream_by_name(
        '$Info')

    test_data_stream = ntfs_data_stream.NTFSDataStream(
        file_entry, fsntfs_data_stream)

    extents = test_data_stream.GetExtents()
    # No extents are returned for a resident $DATA attribute.
    self.assertEqual(len(extents), 0)

  def testIsDefault(self):
    """Test the IsDefault function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\$UpCase', mft_entry=10,
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    test_data_stream = ntfs_data_stream.NTFSDataStream(file_entry, None)

    result = test_data_stream.IsDefault()
    self.assertTrue(result)

    fsntfs_file_entry = file_entry.GetNTFSFileEntry()
    self.assertIsNotNone(fsntfs_file_entry)

    fsntfs_data_stream = fsntfs_file_entry.get_alternate_data_stream_by_name(
        '$Info')

    test_data_stream = ntfs_data_stream.NTFSDataStream(
        file_entry, fsntfs_data_stream)

    result = test_data_stream.IsDefault()
    self.assertFalse(result)


if __name__ == '__main__':
  unittest.main()
