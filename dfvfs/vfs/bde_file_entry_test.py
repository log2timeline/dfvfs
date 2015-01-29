#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using pybde."""

import os
import unittest

import pybde

from dfvfs.file_io import os_file_io
from dfvfs.path import bde_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import bde_file_entry
from dfvfs.vfs import bde_file_system


class BdeFileEntryTest(unittest.TestCase):
  """The unit test for the BDE file entry object."""

  _BDE_PASSWORD = 'bde-TEST'

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join('test_data', 'bdetogo.raw')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._os_file_object = os_file_io.OSFile(self._resolver_context)
    self._os_file_object.open(self._os_path_spec, mode='rb')

    bde_volume = pybde.volume()
    bde_volume.set_password(self._BDE_PASSWORD)
    bde_volume.open_file_object(self._os_file_object)
    self._file_system = bde_file_system.BdeFileSystem(
        self._resolver_context, bde_volume, self._os_path_spec)

  def testIntialize(self):
    """Test the initialize functionality."""
    file_entry = bde_file_entry.BdeFileEntry(
        self._resolver_context, self._os_file_object, self._os_path_spec)

    self.assertNotEquals(file_entry, None)

  def testGetFileEntryByPathSpec(self):
    """Test the get a file entry by path specification functionality."""
    path_spec = bde_path_spec.BdePathSpec(parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)

  def testGetParentFileEntry(self):
    """Test the get parent file entry functionality."""
    path_spec = bde_path_spec.BdePathSpec(parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertEquals(parent_file_entry, None)

  def testGetStat(self):
    """Test the get stat functionality."""
    path_spec = bde_path_spec.BdePathSpec(parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    stat_object = file_entry.GetStat()

    self.assertNotEquals(stat_object, None)
    self.assertEquals(stat_object.type, stat_object.TYPE_FILE)

  def testIsFunctions(self):
    """Test the Is? functionality."""
    path_spec = bde_path_spec.BdePathSpec(parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertTrue(file_entry.IsRoot())
    self.assertTrue(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertFalse(file_entry.IsDirectory())
    self.assertTrue(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

  def testSubFileEntries(self):
    """Test the sub file entries iteration functionality."""
    path_spec = bde_path_spec.BdePathSpec(parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)

    self.assertEquals(file_entry.number_of_sub_file_entries, 0)

    expected_sub_file_entry_names = []

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEquals(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEquals(
        sorted(sub_file_entry_names), expected_sub_file_entry_names)


if __name__ == '__main__':
  unittest.main()
