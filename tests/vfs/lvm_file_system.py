#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for a file system implementation using pyvslvm."""

import os
import unittest

from dfvfs.path import lvm_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import lvm_file_system


class LVMFileSystemTest(unittest.TestCase):
  """The unit test for the LVM file system object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'lvmtest.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    self._lvm_path_spec = lvm_path_spec.LVMPathSpec(
        location=u'/', parent=self._qcow_path_spec)

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

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = lvm_file_system.LVMFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._lvm_path_spec)

    file_system.Close()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = lvm_file_system.LVMFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._lvm_path_spec)

    path_spec = lvm_path_spec.LVMPathSpec(
        location=u'/', parent=self._qcow_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._qcow_path_spec, volume_index=1)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = lvm_path_spec.LVMPathSpec(
        location=u'/lvm2', parent=self._qcow_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._qcow_path_spec, volume_index=9)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = lvm_path_spec.LVMPathSpec(
        location=u'/lvm0', parent=self._qcow_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = lvm_path_spec.LVMPathSpec(
        location=u'/lvm9', parent=self._qcow_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = lvm_file_system.LVMFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._lvm_path_spec)

    path_spec = lvm_path_spec.LVMPathSpec(
        location=u'/', parent=self._qcow_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, u'')

    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._qcow_path_spec, volume_index=1)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, u'lvm2')

    path_spec = lvm_path_spec.LVMPathSpec(
        location=u'/lvm2', parent=self._qcow_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, u'lvm2')

    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._qcow_path_spec, volume_index=9)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    path_spec = lvm_path_spec.LVMPathSpec(
        location=u'/lvm0', parent=self._qcow_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    path_spec = lvm_path_spec.LVMPathSpec(
        location=u'/lvm9', parent=self._qcow_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    file_system.Close()

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = lvm_file_system.LVMFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._lvm_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, u'')

    file_system.Close()


if __name__ == '__main__':
  unittest.main()
