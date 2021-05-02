#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for a file system implementation using pyvshadow."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import vshadow_file_system

from tests import test_lib as shared_test_lib


class VShadowFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests the Volume Shadow Snapshot (VSS) file system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['vss.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._vshadow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, location='/',
        parent=self._raw_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  # vshadowinfo test_data/vss.raw
  # vshadowinfo 20210425
  #
  # Volume Shadow Snapshot information:
  #     Number of stores:	2
  #
  # Store: 1
  #     Identifier          : de81cc22-aa8b-11eb-9339-8cdcd4557abc
  #     Shadow copy set ID  : 6c5c9cd2-ea46-4c70-a4a8-568fdabd27c1
  #     Creation time       : May 01, 2021 17:40:03.223030400 UTC
  #     Shadow copy ID      : 2c6c6cc8-2b97-41da-a030-4add838ae8f6
  #     Volume size         : 78 MiB (82771968 bytes)
  #     Attribute flags     : 0x00420009
  #
  # Store: 2
  #     Identifier          : de81cc2b-aa8b-11eb-9339-8cdcd4557abc
  #     Shadow copy set ID  : b4f4b9d6-1cf2-4bfc-b1a3-c2f6e9628ef9
  #     Creation time       : May 01, 2021 17:41:28.224986300 UTC
  #     Shadow copy ID      : 19e1881a-c184-4ec4-908e-766ba3373e8a
  #     Volume size         : 78 MiB (82771968 bytes)
  #     Attribute flags     : 0x00420009

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = vshadow_file_system.VShadowFileSystem(
        self._resolver_context, self._vshadow_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = vshadow_file_system.VShadowFileSystem(
        self._resolver_context, self._vshadow_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, location='/',
        parent=self._raw_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, parent=self._raw_path_spec,
        store_index=1)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, location='/vss2',
        parent=self._raw_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, parent=self._raw_path_spec,
        store_index=9)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, location='/vss0',
        parent=self._raw_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, location='/vss9',
        parent=self._raw_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = vshadow_file_system.VShadowFileSystem(
        self._resolver_context, self._vshadow_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, location='/',
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, parent=self._raw_path_spec,
        store_index=1)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'vss2')

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, location='/vss2',
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'vss2')

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, parent=self._raw_path_spec,
        store_index=9)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, location='/vss0',
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, location='/vss9',
        parent=self._raw_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = vshadow_file_system.VShadowFileSystem(
        self._resolver_context, self._vshadow_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

  # TODO: add tests for GetVShadowStoreByPathSpec function.


if __name__ == '__main__':
  unittest.main()
