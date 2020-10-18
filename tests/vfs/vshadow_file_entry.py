#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using pyvshadow."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import vshadow_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import vshadow_file_entry
from dfvfs.vfs import vshadow_file_system

from tests import test_lib as shared_test_lib


class VShadowDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the Volume Shadow Snapshot (VSS) directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    self._vshadow_path_spec = vshadow_path_spec.VShadowPathSpec(
        location='/', parent=self._qcow_path_spec)

    self._file_system = vshadow_file_system.VShadowFileSystem(
        self._resolver_context)
    self._file_system.Open(self._vshadow_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = vshadow_file_entry.VShadowDirectory(
        self._file_system, self._vshadow_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = vshadow_file_entry.VShadowDirectory(
        self._file_system, self._vshadow_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 2)


class VShadowFileEntryTest(shared_test_lib.BaseTestCase):
  """Tests the Volume Shadow Snapshot (VSS) file entry."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    self._vshadow_path_spec = vshadow_path_spec.VShadowPathSpec(
        location='/', parent=self._qcow_path_spec)

    self._file_system = vshadow_file_system.VShadowFileSystem(
        self._resolver_context)
    self._file_system.Open(self._vshadow_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  # qcowmount test_data/vsstest.qcow2 fuse/
  # vshadowinfo fuse/qcow1
  #
  # Volume Shadow Snapshot information:
  #   Number of stores:	2
  #
  # Store: 1
  #   ...
  #   Identifier		: 600f0b69-5bdf-11e3-9d6c-005056c00008
  #   Shadow copy set ID	: 0a4e3901-6abb-48fc-95c2-6ab9e38e9e71
  #   Creation time		: Dec 03, 2013 06:35:09.736378700 UTC
  #   Shadow copy ID		: 4e3c03c2-7bc6-4288-ad96-c1eac1a55f71
  #   Volume size		: 1073741824 bytes
  #   Attribute flags		: 0x00420009
  #
  # Store: 2
  #   Identifier		: 600f0b6d-5bdf-11e3-9d6c-005056c00008
  #   Shadow copy set ID	: 8438a0ee-0f06-443b-ac0c-2905647ca5d6
  #   Creation time		: Dec 03, 2013 06:37:48.919058300 UTC
  #   Shadow copy ID		: 18f1ac6e-959d-436f-bdcc-e797a729e290
  #   Volume size		: 1073741824 bytes
  #   Attribute flags		: 0x00420009

  def testIntialize(self):
    """Test the __init__ function."""
    file_entry = vshadow_file_entry.VShadowFileEntry(
        self._resolver_context, self._file_system, self._vshadow_path_spec,
        is_virtual=True)

    self.assertIsNotNone(file_entry)

  # TODO: add tests for _GetDirectory
  # TODO: add tests for _GetSubFileEntries

  def testCreationTime(self):
    """Test the creation_time property."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        parent=self._qcow_path_spec, store_index=1)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertIsNotNone(file_entry.creation_time)

  def testName(self):
    """Test the name property."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        parent=self._qcow_path_spec, store_index=1)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'vss2')

  def testSize(self):
    """Test the size property."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        parent=self._qcow_path_spec, store_index=1)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 1073741824)

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        parent=self._qcow_path_spec, store_index=1)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertIsNotNone(parent_file_entry)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location='/', parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertIsNone(parent_file_entry)

  def testGetStat(self):
    """Tests the GetStat function."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        parent=self._qcow_path_spec, store_index=1)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry.GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 1073741824)

    self.assertEqual(stat_object.crtime, 1386052668)
    self.assertEqual(stat_object.crtime_nano, 9190583)

  # TODO: add tests for GetVShadowStore
  # TODO: add tests for HasExternalData

  def testIsFunctions(self):
    """Test the Is? functions."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        parent=self._qcow_path_spec, store_index=1)
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

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location='/', parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertTrue(file_entry.IsRoot())
    self.assertTrue(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertTrue(file_entry.IsDirectory())
    self.assertFalse(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

  def testSubFileEntries(self):
    """Test the sub file entries iteration functionality."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        location='/', parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 2)

    expected_sub_file_entry_names = ['vss1', 'vss2']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))

  def testDataStreams(self):
    """Test the data streams functionality."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        parent=self._qcow_path_spec, store_index=1)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location='/', parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        parent=self._qcow_path_spec, store_index=1)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = ''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, data_stream_name)

    data_stream = file_entry.GetDataStream('bogus')
    self.assertIsNone(data_stream)


if __name__ == '__main__':
  unittest.main()
