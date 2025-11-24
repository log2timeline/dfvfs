#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for a file system implementation using pyvslvm."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import lvm_file_system

from tests import test_lib as shared_test_lib


class LVMFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests the LVM file system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

    test_path = self._GetTestFilePath(['lvm.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._lvm_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_LVM, location='/',
        parent=self._raw_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  # vslvminfo lvm.raw
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
    file_system = lvm_file_system.LVMFileSystem(
        self._resolver_context, self._lvm_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = lvm_file_system.LVMFileSystem(
        self._resolver_context, self._lvm_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_LVM, location='/',
        parent=self._raw_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_LVM, parent=self._raw_path_spec,
        volume_index=0)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_LVM, location='/lvm1',
        parent=self._raw_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_LVM, parent=self._raw_path_spec,
        volume_index=9)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_LVM, location='/lvm0',
        parent=self._raw_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_LVM, location='/lvm9',
        parent=self._raw_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = lvm_file_system.LVMFileSystem(
        self._resolver_context, self._lvm_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_LVM, location='/',
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_LVM, parent=self._raw_path_spec,
        volume_index=0)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'lvm1')

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_LVM, location='/lvm1',
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'lvm1')

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_LVM, parent=self._raw_path_spec,
        volume_index=9)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_LVM, location='/lvm0',
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_LVM, location='/lvm9',
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = lvm_file_system.LVMFileSystem(
        self._resolver_context, self._lvm_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')


if __name__ == '__main__':
  unittest.main()
