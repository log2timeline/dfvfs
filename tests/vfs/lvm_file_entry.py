#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using pyvslvm."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import lvm_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import raw_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import lvm_file_entry
from dfvfs.vfs import lvm_file_system

from tests import test_lib as shared_test_lib


class LVMDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the LVM directory."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['lvm.raw'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._raw_path_spec = raw_path_spec.RawPathSpec(parent=path_spec)
    self._lvm_path_spec = lvm_path_spec.LVMPathSpec(
        location='/', parent=self._raw_path_spec)

    self._file_system = lvm_file_system.LVMFileSystem(self._resolver_context)
    self._file_system.Open(self._lvm_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = lvm_file_entry.LVMDirectory(
        self._file_system, self._lvm_path_spec)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = lvm_file_entry.LVMDirectory(
        self._file_system, self._lvm_path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 2)


class LVMFileEntryTest(shared_test_lib.BaseTestCase):
  """Tests the LVM file entry."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['lvm.raw'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._raw_path_spec = raw_path_spec.RawPathSpec(parent=path_spec)
    self._lvm_path_spec = lvm_path_spec.LVMPathSpec(
        location='/', parent=self._raw_path_spec)

    self._file_system = lvm_file_system.LVMFileSystem(self._resolver_context)
    self._file_system.Open(self._lvm_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()
    self._resolver_context.Empty()

  # vslvminfo fuse/lvm.raw
  #
  # Linux Logical Volume Manager (LVM) information:
  # Volume Group (VG):
  #   Name:                         test_volume_group
  #   Identifier:                   SN0dH9-7Eic-NCvi-WHj8-76G8-za0g-iJobeq
  #   Sequence number:              2
  #   Extent size:                  4.0 MiB (4194304 bytes)
  #   Number of physical volumes:   1
  #   Number of logical volumes:    1
  #
  # Physical Volume (PV): 1
  #   Name:                         pv0
  #   Identifier:                   K994MB-Sn1r-7rpS-hQEW-DgUP-87Dr-9d0MFa
  #   Device path:                  /dev/loop0
  #   Volume size:                  8.0 MiB (8388608 bytes)
  #
  # Logical Volume (LV): 1
  #   Name:                         test_logical_volume
  #   Identifier:                   0MUZZr-7jgO-iFwW-sSG3-Rb8W-w5td-qAOF8e
  #   Number of segments:           1
  #   Segment: 1
  #     Offset:                     0x00000000 (0)
  #     Size:                       4.0 MiB (4194304 bytes)
  #     Number of stripes:          1
  #     Stripe: 1
  #       Physical volume:          pv0
  #       Data area offset:         0x00000000 (0)

  def testIntialize(self):
    """Test the __init__ function."""
    file_entry = lvm_file_entry.LVMFileEntry(
        self._resolver_context, self._file_system, self._lvm_path_spec,
        is_virtual=True)

    self.assertIsNotNone(file_entry)

  # TODO: test _GetDirectory
  # TODO: test _GetSubFileEntries

  def testName(self):
    """Test the name property."""
    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._raw_path_spec, volume_index=0)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'lvm1')

  def testSize(self):
    """Test the size property."""
    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._raw_path_spec, volume_index=0)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 4194304)

  # TODO: test GetLVMLogicalVolume

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._raw_path_spec, volume_index=0)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertIsNotNone(parent_file_entry)

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertIsNone(parent_file_entry)

  def testGetStat(self):
    """Tests the GetStat function."""
    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._raw_path_spec, volume_index=0)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    stat_object = file_entry.GetStat()

    self.assertIsNotNone(stat_object)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)
    self.assertEqual(stat_object.size, 4194304)

    # TODO: implement in pyvslvm
    # self.assertEqual(stat_object.crtime, 0)
    # self.assertEqual(stat_object.crtime_nano, 0)

  def testIsFunctions(self):
    """Test the Is? functions."""
    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._raw_path_spec, volume_index=0)
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

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/', parent=self._raw_path_spec)
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
    path_spec = lvm_path_spec.LVMPathSpec(
        location='/', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 2)

    expected_sub_file_entry_names = ['lvm1', 'lvm2']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))

  def testDataStreams(self):
    """Test the data streams functionality."""
    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._raw_path_spec, volume_index=0)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._raw_path_spec, volume_index=0)
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
