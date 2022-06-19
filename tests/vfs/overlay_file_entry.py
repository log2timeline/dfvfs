#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Overlay file entry implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import overlay_file_entry
from dfvfs.vfs import overlay_file_system
from dfvfs.vfs import ext_attribute
from dfvfs.vfs import xfs_attribute
from tests import test_lib as shared_test_lib


class OverlayFileEntryTestWithEXT4(shared_test_lib.BaseTestCase):
  """Tests the Overlay file entry."""

  # pylint: disable=protected-access

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['overlay_ext4.dd'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._lower_path_spec = [path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, location='/lower',
        parent=self._raw_path_spec)]
    self._upper_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, location='/upper',
        parent=self._raw_path_spec)
    self._overlay_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/')

    self._file_system = overlay_file_system.OverlayFileSystem(
        self._resolver_context, self._overlay_path_spec,
        self._lower_path_spec, self._upper_path_spec)
    self._file_system.Open()

    self._ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, parent=self._raw_path_spec,
        location='/upper/c.txt', inode=25)
    self._test_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/c.txt',
        parent=self._ext_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    file_entry = overlay_file_entry.OverlayFileEntry(
        self._resolver_context, self._file_system, self._test_path_spec)

    self.assertIsNotNone(file_entry)

  def testAccessTime(self):
    """Test the access_time property."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._test_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.access_time)

  def testChangeTime(self):
    """Test the change_time property."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._test_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.change_time)

  def testCreationTime(self):
    """Test the creation_time property."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._test_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNone(file_entry.creation_time)

  def testModificationTime(self):
    """Test the modification_time property."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._test_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.modification_time)

  def testGetAttributes(self):
    """Tests the _GetAttributes function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._test_path_spec)
    self.assertIsNotNone(file_entry)

    self.assertIsNone(file_entry._attributes)

    file_entry._GetAttributes()
    self.assertIsNotNone(file_entry._attributes)
    self.assertEqual(len(file_entry._attributes), 1)

    test_attribute = file_entry._attributes[0]
    self.assertIsInstance(test_attribute, ext_attribute.EXTExtendedAttribute)
    self.assertEqual(test_attribute.name, 'user.myxattr1')

    test_attribute_value_data = test_attribute.read()
    self.assertEqual(test_attribute_value_data, b'upper extended attribute')

  def testGetStat(self):
    """Tests the _GetStat function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._test_path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry._GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 9)

    self.assertEqual(stat_object.mode, 420)
    self.assertEqual(stat_object.uid, 0)
    self.assertEqual(stat_object.gid, 0)

    self.assertEqual(stat_object.atime, 1650628823)
    self.assertFalse(hasattr(stat_object, 'atime_nano'))

    self.assertEqual(stat_object.ctime, 1650628823)
    self.assertFalse(hasattr(stat_object, 'ctime_nano'))

    self.assertFalse(hasattr(stat_object, 'crtime'))

    self.assertEqual(stat_object.mtime, 1650628823)
    self.assertFalse(hasattr(stat_object, 'mtime_nano'))

  def testGetStatAttribute(self):
    """Tests the _GetStatAttribute function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._test_path_spec)
    self.assertIsNotNone(file_entry)

    stat_attribute = file_entry._GetStatAttribute()

    self.assertIsNotNone(stat_attribute)
    self.assertEqual(stat_attribute.group_identifier, 0)
    self.assertEqual(stat_attribute.inode_number, 25)
    self.assertEqual(stat_attribute.mode, 0o100644)
    self.assertEqual(stat_attribute.number_of_links, 1)
    self.assertEqual(stat_attribute.owner_identifier, 0)
    self.assertEqual(stat_attribute.size, 9)
    self.assertEqual(stat_attribute.type, stat_attribute.TYPE_FILE)

  def testGetExtents(self):
    """Tests the GetExtents function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._test_path_spec)
    self.assertIsNotNone(file_entry)

    extents = file_entry.GetExtents()
    self.assertEqual(len(extents), 1)

    self.assertEqual(extents[0].extent_type, definitions.EXTENT_TYPE_DATA)
    self.assertEqual(extents[0].offset, 8396800)
    self.assertEqual(extents[0].size, 4096)

    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, inode=26,
        location='/upper/testdir', parent=self._raw_path_spec)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/testdir',
        parent=ext_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    extents = file_entry.GetExtents()
    self.assertEqual(len(extents), 0)

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, inode=26,
        location='/upper/testdir', parent=self._raw_path_spec)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/testdir',
        parent=ext_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

  def testGetLinkedFileEntry(self):
    """Tests the GetLinkedFileEntry function."""
    # TODO:  need test data

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, inode=27,
        location='/upper/testdir/d.txt', parent=self._raw_path_spec)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/testdir/d.txt',
        parent=ext_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, 'testdir')

    # TODO - propertly check parent

  def testIsFunctions(self):
    """Tests the Is? functions."""
    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, inode=27,
        location='/upper/testdir/d.txt', parent=self._raw_path_spec)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/testdir/d.txt',
        parent=ext_path_spec)
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

    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, inode=26,
        location='/upper/testdir', parent=self._raw_path_spec)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/testdir',
        parent=ext_path_spec)
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

  def testSubFileEntries(self):
    """Tests the number_of_sub_file_entries and sub_file_entries properties."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/')
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.number_of_sub_file_entries, 5)

    expected_sub_file_entry_names = [
        'a.txt',
        'c.txt',
        'testdir',
        'newdir',
        'replacedir']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))

  def testDataStreams(self):
    """Tests the data streams functionality."""
    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, inode=27,
        location='/upper/testdir/d.txt', parent=self._raw_path_spec)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/testdir/d.txt',
        parent=ext_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, inode=26,
        location='/upper/testdir', parent=self._raw_path_spec)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/testdir',
        parent=ext_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, inode=27,
        location='/upper/testdir/d.txt', parent=self._raw_path_spec)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/testdir/d.txt',
        parent=ext_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = ''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)


class OverlayFileEntryTestWithXFS(shared_test_lib.BaseTestCase):
  """Tests the Overlay file entry."""

  # pylint: disable=protected-access

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['overlay_xfs.dd'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._lower_path_spec = [path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, location='/lower',
        parent=self._raw_path_spec)]
    self._upper_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, location='/upper',
        parent=self._raw_path_spec)
    self._overlay_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/')

    self._file_system = overlay_file_system.OverlayFileSystem(
        self._resolver_context, self._overlay_path_spec,
        self._lower_path_spec, self._upper_path_spec)
    self._file_system.Open()

    self._xfs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, parent=self._raw_path_spec,
        location='/upper/c.txt', inode=11088)
    self._test_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/c.txt',
        parent=self._xfs_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    file_entry = overlay_file_entry.OverlayFileEntry(
        self._resolver_context, self._file_system, self._test_path_spec)

    self.assertIsNotNone(file_entry)

  def testAccessTime(self):
    """Test the access_time property."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._test_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.access_time)

  def testChangeTime(self):
    """Test the change_time property."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._test_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.change_time)

  def testCreationTime(self):
    """Test the creation_time property."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._test_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.creation_time)

  def testModificationTime(self):
    """Test the modification_time property."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._test_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.modification_time)

  def testGetAttributes(self):
    """Tests the _GetAttributes function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._test_path_spec)
    self.assertIsNotNone(file_entry)

    self.assertIsNone(file_entry._attributes)

    file_entry._GetAttributes()
    self.assertIsNotNone(file_entry._attributes)
    self.assertEqual(len(file_entry._attributes), 1)

    test_attribute = file_entry._attributes[0]
    self.assertIsInstance(test_attribute, xfs_attribute.XFSExtendedAttribute)
    self.assertEqual(test_attribute.name, 'user.myxattr1')

    test_attribute_value_data = test_attribute.read()
    self.assertEqual(test_attribute_value_data, b'upper extended attribute')

  def testGetStat(self):
    """Tests the _GetStat function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._test_path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry._GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 9)

    self.assertEqual(stat_object.mode, 420)
    self.assertEqual(stat_object.uid, 0)
    self.assertEqual(stat_object.gid, 0)

    self.assertEqual(stat_object.atime, 1650628826)
    self.assertEqual(stat_object.atime_nano, 4851118)

    self.assertEqual(stat_object.ctime, 1650628826)
    self.assertEqual(stat_object.ctime_nano, 4891116)

    self.assertEqual(stat_object.crtime, 1650628826)
    self.assertEqual(stat_object.ctime_nano, 4891116)

    self.assertEqual(stat_object.mtime, 1650628826)
    self.assertEqual(stat_object.mtime_nano, 4851118)

  def testGetStatAttribute(self):
    """Tests the _GetStatAttribute function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._test_path_spec)
    self.assertIsNotNone(file_entry)

    stat_attribute = file_entry._GetStatAttribute()

    self.assertIsNotNone(stat_attribute)
    self.assertEqual(stat_attribute.group_identifier, 0)
    self.assertEqual(stat_attribute.inode_number, 11088)
    self.assertEqual(stat_attribute.mode, 0o100644)
    self.assertEqual(stat_attribute.number_of_links, 1)
    self.assertEqual(stat_attribute.owner_identifier, 0)
    self.assertEqual(stat_attribute.size, 9)
    self.assertEqual(stat_attribute.type, stat_attribute.TYPE_FILE)

  def testGetExtents(self):
    """Tests the GetExtents function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._test_path_spec)
    self.assertIsNotNone(file_entry)

    extents = file_entry.GetExtents()
    self.assertEqual(len(extents), 1)

    self.assertEqual(extents[0].extent_type, definitions.EXTENT_TYPE_DATA)
    self.assertEqual(extents[0].offset, 5656576)
    self.assertEqual(extents[0].size, 4096)

    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, inode=11089,
        location='/upper/testdir', parent=self._raw_path_spec)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/testdir',
        parent=ext_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    extents = file_entry.GetExtents()
    self.assertEqual(len(extents), 0)

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, inode=11089,
        location='/upper/testdir', parent=self._raw_path_spec)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/testdir',
        parent=ext_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

  def testGetLinkedFileEntry(self):
    """Tests the GetLinkedFileEntry function."""
    # TODO:  need test data

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, inode=11090,
        location='/upper/testdir/d.txt', parent=self._raw_path_spec)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/testdir/d.txt',
        parent=ext_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertIsNotNone(parent_file_entry)

    self.assertEqual(parent_file_entry.name, 'testdir')

    # TODO - propertly check parent

  def testIsFunctions(self):
    """Tests the Is? functions."""
    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, inode=11090,
        location='/upper/testdir/d.txt', parent=self._raw_path_spec)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/testdir/d.txt',
        parent=ext_path_spec)
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

    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, inode=11089,
        location='/upper/testdir', parent=self._raw_path_spec)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/testdir',
        parent=ext_path_spec)
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

  def testSubFileEntries(self):
    """Tests the number_of_sub_file_entries and sub_file_entries properties."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/')
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.number_of_sub_file_entries, 5)

    expected_sub_file_entry_names = [
        'a.txt',
        'c.txt',
        'testdir',
        'newdir',
        'replacedir']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)
    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))

  def testDataStreams(self):
    """Tests the data streams functionality."""
    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, inode=11090,
        location='/upper/testdir/d.txt', parent=self._raw_path_spec)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/testdir/d.txt',
        parent=ext_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, inode=11089,
        location='/upper/testdir', parent=self._raw_path_spec)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/testdir',
        parent=ext_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    xfs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, inode=11090,
        location='/upper/testdir/d.txt', parent=self._raw_path_spec)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/testdir/d.txt',
        parent=xfs_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)
    data_stream_name = ''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)


if __name__ == '__main__':
  unittest.main()
