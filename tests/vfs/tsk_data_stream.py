#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the data stream implementation using pytsk3."""

import unittest

import pytsk3

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import tsk_data_stream
from dfvfs.vfs import tsk_file_system

from tests import test_lib as shared_test_lib


class TSKDataStreamTestExt2(shared_test_lib.BaseTestCase):
  """Tests the SleuthKit (TSK) data stream on ext2."""

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

  def testName(self):
    """Test the name property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    test_data_stream = tsk_data_stream.TSKDataStream(file_entry, None)
    self.assertEqual(test_data_stream.name, '')

  def testGetExtents(self):
    """Test the GetExtents function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    test_data_stream = tsk_data_stream.TSKDataStream(file_entry, None)

    extents = test_data_stream.GetExtents()
    self.assertEqual(len(extents), 1)

    self.assertEqual(extents[0].extent_type, definitions.EXTENT_TYPE_DATA)
    self.assertEqual(extents[0].offset, 527360)
    self.assertEqual(extents[0].size, 1024)

  def testIsDefault(self):
    """Test the IsDefault function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    test_data_stream = tsk_data_stream.TSKDataStream(file_entry, None)

    result = test_data_stream.IsDefault()
    self.assertTrue(result)


class TSKDataStreamTestHFSPlus(shared_test_lib.BaseTestCase):
  """Tests the SleuthKit (TSK) data stream on HFS+."""

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

  def _GetResourceForkAttribute(self, tsk_file):
    """Retrieves an resource fork attribute.

    Args:
      tsk_file (pytsk3.File): TSK file.

    Returns:
      pytsk3.Attribute: TSK attribute or None.
    """
    for tsk_attribute in tsk_file:
      if getattr(tsk_attribute, 'info', None):
        attribute_type = getattr(tsk_attribute.info, 'type', None)
        if attribute_type == pytsk3.TSK_FS_ATTR_TYPE_HFS_RSRC:
          return tsk_attribute

    return None

  def testName(self):
    """Test the name property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=25,
        location='/a_directory/a_resourcefork', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    test_data_stream = tsk_data_stream.TSKDataStream(file_entry, None)
    self.assertEqual(test_data_stream.name, '')

    tsk_file = file_entry.GetTSKFile()
    self.assertIsNotNone(tsk_file)

    tsk_attribute = self._GetResourceForkAttribute(tsk_file)
    self.assertIsNotNone(tsk_attribute)

    test_data_stream = tsk_data_stream.TSKDataStream(file_entry, tsk_attribute)
    self.assertEqual(test_data_stream.name, 'rsrc')

  def testGetExtents(self):
    """Test the GetExtents function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=25,
        location='/a_directory/a_resourcefork', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    test_data_stream = tsk_data_stream.TSKDataStream(file_entry, None)

    extents = test_data_stream.GetExtents()
    self.assertEqual(len(extents), 0)

    tsk_file = file_entry.GetTSKFile()
    self.assertIsNotNone(tsk_file)

    tsk_attribute = self._GetResourceForkAttribute(tsk_file)
    self.assertIsNotNone(tsk_attribute)

    test_data_stream = tsk_data_stream.TSKDataStream(file_entry, tsk_attribute)

    extents = test_data_stream.GetExtents()
    self.assertEqual(len(extents), 1)

    self.assertEqual(extents[0].extent_type, definitions.EXTENT_TYPE_DATA)
    self.assertEqual(extents[0].offset, 1142784)
    self.assertEqual(extents[0].size, 4096)

  def testIsDefault(self):
    """Test the IsDefault function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=25,
        location='/a_directory/a_resourcefork', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    test_data_stream = tsk_data_stream.TSKDataStream(file_entry, None)

    result = test_data_stream.IsDefault()
    self.assertTrue(result)

    tsk_file = file_entry.GetTSKFile()
    self.assertIsNotNone(tsk_file)

    tsk_attribute = self._GetResourceForkAttribute(tsk_file)
    self.assertIsNotNone(tsk_attribute)

    test_data_stream = tsk_data_stream.TSKDataStream(file_entry, tsk_attribute)

    result = test_data_stream.IsDefault()
    self.assertFalse(result)


class TSKDataStreamTestNTFS(shared_test_lib.BaseTestCase):
  """Tests the SleuthKit (TSK) data stream on NTFS."""

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

  def _GetAlternateDataStreamAttribute(self, tsk_file):
    """Retrieves an ADS attribute.

    Args:
      tsk_file (pytsk3.File): TSK file.

    Returns:
      pytsk3.Attribute: TSK attribute or None.
    """
    for tsk_attribute in tsk_file:
      if getattr(tsk_attribute, 'info', None):
        attribute_name = getattr(tsk_attribute.info, 'name', None)
        attribute_type = getattr(tsk_attribute.info, 'type', None)
        if (attribute_type == pytsk3.TSK_FS_ATTR_TYPE_NTFS_DATA and
            attribute_name):
          return tsk_attribute

    return None

  def testName(self):
    """Test the name property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=10, location='/$UpCase',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    test_data_stream = tsk_data_stream.TSKDataStream(file_entry, None)
    self.assertEqual(test_data_stream.name, '')

    tsk_file = file_entry.GetTSKFile()
    self.assertIsNotNone(tsk_file)

    tsk_attribute = self._GetAlternateDataStreamAttribute(tsk_file)
    self.assertIsNotNone(tsk_attribute)

    test_data_stream = tsk_data_stream.TSKDataStream(file_entry, tsk_attribute)
    self.assertEqual(test_data_stream.name, '$Info')

  def testGetExtents(self):
    """Test the GetExtents function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=10, location='/$UpCase',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    test_data_stream = tsk_data_stream.TSKDataStream(file_entry, None)

    extents = test_data_stream.GetExtents()
    self.assertEqual(len(extents), 1)

    self.assertEqual(extents[0].extent_type, definitions.EXTENT_TYPE_DATA)
    self.assertEqual(extents[0].offset, 823296)
    self.assertEqual(extents[0].size, 131072)

    tsk_file = file_entry.GetTSKFile()
    self.assertIsNotNone(tsk_file)

    tsk_attribute = self._GetAlternateDataStreamAttribute(tsk_file)
    self.assertIsNotNone(tsk_attribute)

    test_data_stream = tsk_data_stream.TSKDataStream(file_entry, tsk_attribute)

    extents = test_data_stream.GetExtents()
    # No extents are returned for a resident $DATA attribute.
    self.assertEqual(len(extents), 0)

  def testIsDefault(self):
    """Test the IsDefault function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=10, location='/$UpCase',
        parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    test_data_stream = tsk_data_stream.TSKDataStream(file_entry, None)

    result = test_data_stream.IsDefault()
    self.assertTrue(result)

    tsk_file = file_entry.GetTSKFile()
    self.assertIsNotNone(tsk_file)

    tsk_attribute = self._GetAlternateDataStreamAttribute(tsk_file)
    self.assertIsNotNone(tsk_attribute)

    test_data_stream = tsk_data_stream.TSKDataStream(file_entry, tsk_attribute)

    result = test_data_stream.IsDefault()
    self.assertFalse(result)


if __name__ == '__main__':
  unittest.main()
