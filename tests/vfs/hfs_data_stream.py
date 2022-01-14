#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the data stream implementation using pyfshfs."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import hfs_data_stream
from dfvfs.vfs import hfs_file_system

from tests import test_lib as shared_test_lib


class HFSDataStreamTest(shared_test_lib.BaseTestCase):
  """Tests the HFS data stream."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['hfsplus.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._hfs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS, location='/',
        parent=self._raw_path_spec)

    self._file_system = hfs_file_system.HFSFileSystem(
        self._resolver_context, self._hfs_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testName(self):
    """Test the name property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS, identifier=25,
        location='/a_directory/a_resourcefork', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    test_data_stream = hfs_data_stream.HFSDataStream(file_entry, None)
    self.assertEqual(test_data_stream.name, '')

    fshfs_file_entry = file_entry.GetHFSFileEntry()
    self.assertIsNotNone(fshfs_file_entry)

    fshfs_data_stream = fshfs_file_entry.get_resource_fork()

    test_data_stream = hfs_data_stream.HFSDataStream(
        file_entry, fshfs_data_stream)
    self.assertEqual(test_data_stream.name, 'rsrc')

  def testGetExtents(self):
    """Test the GetExtents function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS, identifier=25,
        location='/a_directory/a_resourcefork', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    test_data_stream = hfs_data_stream.HFSDataStream(file_entry, None)

    extents = test_data_stream.GetExtents()
    self.assertEqual(len(extents), 0)

    fshfs_file_entry = file_entry.GetHFSFileEntry()
    self.assertIsNotNone(fshfs_file_entry)

    fshfs_data_stream = fshfs_file_entry.get_resource_fork()

    test_data_stream = hfs_data_stream.HFSDataStream(
        file_entry, fshfs_data_stream)

    extents = test_data_stream.GetExtents()
    self.assertEqual(len(extents), 1)

    self.assertEqual(extents[0].extent_type, definitions.EXTENT_TYPE_DATA)
    self.assertEqual(extents[0].offset, 1142784)
    self.assertEqual(extents[0].size, 4096)

  def testIsDefault(self):
    """Test the IsDefault function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS, identifier=25,
        location='/a_directory/a_resourcefork', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    test_data_stream = hfs_data_stream.HFSDataStream(file_entry, None)

    result = test_data_stream.IsDefault()
    self.assertTrue(result)

    fshfs_file_entry = file_entry.GetHFSFileEntry()
    self.assertIsNotNone(fshfs_file_entry)

    fshfs_data_stream = fshfs_file_entry.get_resource_fork()

    test_data_stream = hfs_data_stream.HFSDataStream(
        file_entry, fshfs_data_stream)

    result = test_data_stream.IsDefault()
    self.assertFalse(result)


if __name__ == '__main__':
  unittest.main()
