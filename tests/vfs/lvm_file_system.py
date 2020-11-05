#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for a file system implementation using pyvslvm."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import lvm_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import raw_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import lvm_file_system

from tests import test_lib as shared_test_lib


class LVMFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests the LVM file system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['lvm.raw'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._raw_path_spec = raw_path_spec.RawPathSpec(parent=path_spec)
    self._lvm_path_spec = lvm_path_spec.LVMPathSpec(
        location='/', parent=self._raw_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
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
        location='/', parent=self._raw_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._raw_path_spec, volume_index=0)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/lvm1', parent=self._raw_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._raw_path_spec, volume_index=9)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/lvm0', parent=self._raw_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/lvm9', parent=self._raw_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = lvm_file_system.LVMFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._lvm_path_spec)

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/', parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._raw_path_spec, volume_index=0)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'lvm1')

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/lvm1', parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'lvm1')

    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._raw_path_spec, volume_index=9)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/lvm0', parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/lvm9', parent=self._raw_path_spec)
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
    self.assertEqual(file_entry.name, '')

    file_system.Close()


if __name__ == '__main__':
  unittest.main()
