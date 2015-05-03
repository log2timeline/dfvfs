#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the operating system file entry implementation."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import os_file_entry
from dfvfs.vfs import os_file_system


class OSFileEntryTest(unittest.TestCase):
  """The unit test for the operating system file entry object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'testdir_os')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)

    self._file_system = os_file_system.OSFileSystem(self._resolver_context)
    self._file_system.Open(path_spec=self._os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()

  def testIntialize(self):
    """Test the initialize functionality."""
    file_entry = os_file_entry.OSFileEntry(
        self._resolver_context, self._file_system, self._os_path_spec)

    self.assertNotEqual(file_entry, None)

  def testGetFileEntryByPathSpec(self):
    """Test the get a file entry by path specification functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._os_path_spec)

    self.assertNotEqual(file_entry, None)

  def testGetParentFileEntry(self):
    """Test the get parent file entry functionality."""
    test_file = os.path.join('test_data', 'testdir_os', 'file1.txt')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEqual(file_entry, None)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertNotEqual(parent_file_entry, None)

    self.assertEqual(parent_file_entry.name, u'testdir_os')

  def testGetStat(self):
    """Test the get stat functionality."""
    test_file = os.path.join('test_data', 'testdir_os', 'file1.txt')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEqual(file_entry, None)

    stat_object = file_entry.GetStat()

    self.assertNotEqual(stat_object, None)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)

  def testIsFunctions(self):
    """Test the Is? functionality."""
    test_file = os.path.join('test_data', 'testdir_os', 'file1.txt')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEqual(file_entry, None)

    self.assertFalse(file_entry.IsRoot())
    self.assertFalse(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertFalse(file_entry.IsDirectory())
    self.assertTrue(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

    test_file = os.path.join('test_data', 'testdir_os')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEqual(file_entry, None)

    self.assertFalse(file_entry.IsRoot())
    self.assertFalse(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertTrue(file_entry.IsDirectory())
    self.assertFalse(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

  def testSubFileEntries(self):
    """Test the sub file entries iteration functionality."""
    file_entry = self._file_system.GetFileEntryByPathSpec(self._os_path_spec)

    self.assertNotEqual(file_entry, None)

    self.assertEqual(file_entry.number_of_sub_file_entries, 5)

    expected_sub_file_entry_names = [
        u'file1.txt', u'file2.txt', u'file3.txt', u'file4.txt', u'file5.txt']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), expected_sub_file_entry_names)


if __name__ == '__main__':
  unittest.main()
