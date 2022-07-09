#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using pyluksde."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import luksde_file_entry
from dfvfs.vfs import luksde_file_system

from tests import test_lib as shared_test_lib


class LUKSDEFileEntryTest(shared_test_lib.BaseTestCase):
  """Tests the LUKSDE file entry."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

    test_path = self._GetTestFilePath(['luks1.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._luksde_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_LUKSDE, parent=test_raw_path_spec)

    self._file_system = luksde_file_system.LUKSDEFileSystem(
        self._resolver_context, self._luksde_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testIntialize(self):
    """Test the __init__ function."""
    file_entry = luksde_file_entry.LUKSDEFileEntry(
        self._resolver_context, self._file_system, self._luksde_path_spec)
    self.assertIsNotNone(file_entry)

    # TODO: test raises.

  def testDataStreams(self):
    """Test the data streams property."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._luksde_path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

  def testSize(self):
    """Test the size property."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._luksde_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 8388608)

  def testSubFileEntries(self):
    """Test the sub file entries property."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._luksde_path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 0)

    expected_sub_file_entry_names = []

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), expected_sub_file_entry_names)

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._luksde_path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = ''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, data_stream_name)

    data_stream = file_entry.GetDataStream('bogus')
    self.assertIsNone(data_stream)

  def testGetFileEntryByPathSpec(self):
    """Test the get a file entry by path specification functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._luksde_path_spec)
    self.assertIsNotNone(file_entry)

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._luksde_path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertIsNone(parent_file_entry)

  def testIsFunctions(self):
    """Test the Is? functions."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._luksde_path_spec)
    self.assertIsNotNone(file_entry)

    self.assertTrue(file_entry.IsRoot())
    self.assertTrue(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertFalse(file_entry.IsDirectory())
    self.assertTrue(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

  def testIsLocked(self):
    """Tests the IsLocked function."""
    file_entry = self._file_system.GetFileEntryByPathSpec(
        self._luksde_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsLocked())


if __name__ == '__main__':
  unittest.main()
