#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using pyfvde."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import cs_file_entry
from dfvfs.vfs import cs_file_system

from tests import test_lib as shared_test_lib


class CSFileEntryTest(shared_test_lib.BaseTestCase):
  """Tests the CS file entry."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

    test_path = self._GetTestFilePath(['fvdetest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_qcow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_QCOW, parent=test_os_path_spec)
    self._gpt_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GPT, location='/p1',
        parent=test_qcow_path_spec)
    self._cs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, parent=self._gpt_path_spec)

    self._file_system = cs_file_system.CSFileSystem(
        self._resolver_context, self._cs_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  # fvdeinfo -o $(( 40 * 512 )) fuse/qcow1
  # fvdeinfo 20220120
  #
  # Logical volume: 1 is locked and a password is needed to unlock it.
  #
  # Password:
  #
  # Core Storage information:
  #
  # Logical volume group:
  #     Identifier                  : 94923b58-9f31-4988-8707-cb90c8e45a46
  #     Name                        : TESTLVG
  #     Number of physical volumes  : 1
  #     Number of logical volumes   : 1
  #
  # Physical volume: 1
  #     Identifier                  : 3273a055-3b8b-47e8-b970-df35eecda81b
  #     Size                        : 511 MiB (536829952 bytes)
  #     Encryption method           : AES-XTS
  #
  # Logical volume: 1
  #     Identifier                  : 420af122-cf73-4a30-8b0a-a593a65fbef5
  #     Name                        : TestLV
  #     Size                        : 160 MiB (167772160 bytes)

  def testIntialize(self):
    """Test the __init__ function."""
    file_entry = cs_file_entry.CSFileEntry(
        self._resolver_context, self._file_system, self._cs_path_spec,
        is_virtual=True)

    self.assertIsNotNone(file_entry)

  # TODO: test _GetDirectory
  # TODO: test _GetSubFileEntries

  def testDataStreams(self):
    """Test the data streams property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, parent=self._gpt_path_spec,
        volume_index=0)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [''])

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, location='/',
        parent=self._gpt_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

  def testName(self):
    """Test the name property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, parent=self._gpt_path_spec,
        volume_index=0)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'cs1')

  def testSize(self):
    """Test the size property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, parent=self._gpt_path_spec,
        volume_index=0)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.size, 167772160)

  def testSubFileEntries(self):
    """Test the sub file entries property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, location='/',
        parent=self._gpt_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertEqual(file_entry.number_of_sub_file_entries, 1)

    expected_sub_file_entry_names = ['cs1']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))

  def testGetDataStream(self):
    """Tests the GetDataStream function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, parent=self._gpt_path_spec,
        volume_index=0)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    data_stream_name = ''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertIsNotNone(data_stream)
    self.assertEqual(data_stream.name, data_stream_name)

    data_stream = file_entry.GetDataStream('bogus')
    self.assertIsNone(data_stream)

  # TODO: test GetFVDELogicalVolume

  def testGetParentFileEntry(self):
    """Tests the GetParentFileEntry function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, parent=self._gpt_path_spec,
        volume_index=0)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertIsNotNone(parent_file_entry)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, location='/',
        parent=self._gpt_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    parent_file_entry = file_entry.GetParentFileEntry()
    self.assertIsNone(parent_file_entry)

  def testIsFunctions(self):
    """Test the Is? functions."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, parent=self._gpt_path_spec,
        volume_index=0)
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

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, location='/',
        parent=self._gpt_path_spec)
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

  def testIsLocked(self):
    """Tests the IsLocked function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, parent=self._gpt_path_spec,
        volume_index=0)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertTrue(file_entry.IsLocked())


if __name__ == '__main__':
  unittest.main()
