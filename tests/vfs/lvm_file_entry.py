#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using pyvslvm."""

import os
import unittest

from dfvfs.path import lvm_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import lvm_file_entry
from dfvfs.vfs import lvm_file_system


class LVMFileEntryTest(unittest.TestCase):
  """The unit test for the LVM file entry object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'lvmtest.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    self._lvm_path_spec = lvm_path_spec.LVMPathSpec(
        location=u'/', parent=self._qcow_path_spec)

    self._file_system = lvm_file_system.LVMFileSystem(self._resolver_context)
    self._file_system.Open(self._lvm_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()

  # qcowmount test_data/lvmtest.qcow2 fuse/
  # vslvminfo fuse/qcow1
  #
  # Linux Logical Volume Manager (LVM) information:
  # Volume Group (VG):
  #   Name:                       vg_test
  #   Identifier:                 kZ4S06-lhFY-G4cB-8OQx-SWVg-GrI6-1jEYEf
  #   Sequence number:            3
  #   Extent size:                4194304 bytes
  #   Number of physical volumes: 1
  #   Number of logical volumes:  2
  #
  # Physical Volume (PV): 1
  #   Name:                       pv0
  #   Identifier:                 btEzLa-i0aL-sfS8-Ae9P-QKGU-IhtA-CkpWm7
  #   Device path:                /dev/loop1
  #   Volume size:                16777216 bytes
  #
  # Logical Volume (LV): 1
  #   Name:                       lv_test1
  #   Identifier:                 ldAb7Y-GU1t-qDml-VkAp-qt46-0meR-qJS3vC
  #   Number of segments:         1
  #   Segment: 1
  #     Offset:                   0x00000000 (0)
  #     Size:                     8.0 MiB (8388608 bytes)
  #     Number of stripes:        1
  #     Stripe: 1
  #       Physical volume:        pv0
  #       Data area offset:       0x00000000 (0)
  #
  # Logical Volume (LV): 2
  #   Name:                       lv_test2
  #   Identifier:                 bJxmc8-JEMZ-jXT9-oVeY-40AY-ROro-mCO8Zz
  #   Number of segments:         1
  #   Segment: 1
  #     Offset:                   0x00000000 (0)
  #     Size:                     4.0 MiB (4194304 bytes)
  #     Number of stripes:        1
  #     Stripe: 1
  #       Physical volume:        pv0
  #       Data area offset:       0x00800000 (8388608)

  def testIntialize(self):
    """Test the initialize functionality."""
    file_entry = lvm_file_entry.LVMFileEntry(
        self._resolver_context, self._file_system, self._lvm_path_spec)

    self.assertIsNotNone(file_entry)

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._qcow_path_spec, volume_index=1)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertIsNotNone(parent_file_entry)

    path_spec = lvm_path_spec.LVMPathSpec(
        location=u'/', parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertIsNone(parent_file_entry)

  def testGetStat(self):
    """Tests the GetStat function."""
    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._qcow_path_spec, volume_index=1)
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
        parent=self._qcow_path_spec, volume_index=1)
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
        location=u'/', parent=self._qcow_path_spec)
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
        location=u'/', parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 2)

    expected_sub_file_entry_names = [u'lvm1', u'lvm2']

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
        parent=self._qcow_path_spec, volume_index=1)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [u''])

    path_spec = lvm_path_spec.LVMPathSpec(
        location=u'/', parent=self._qcow_path_spec)
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
        parent=self._qcow_path_spec, volume_index=1)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = u''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, data_stream_name)

    data_stream = file_entry.GetDataStream(u'bogus')
    self.assertIsNone(data_stream)


if __name__ == '__main__':
  unittest.main()
