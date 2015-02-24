#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using the SleuthKit (TSK)."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import tsk_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import tsk_file_entry
from dfvfs.vfs import tsk_file_system


class TSKFileEntryTest(unittest.TestCase):
  """The unit test for the SleuthKit (TSK) file entry object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'ímynd.dd')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._tsk_path_spec = tsk_path_spec.TSKPathSpec(
        location=u'/', parent=self._os_path_spec)

    self._file_system = tsk_file_system.TSKFileSystem(self._resolver_context)
    self._file_system.Open(path_spec=self._tsk_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()

  def testIntialize(self):
    """Test the initialize functionality."""
    file_entry = tsk_file_entry.TSKFileEntry(
        self._resolver_context, self._file_system, self._tsk_path_spec)

    self.assertNotEquals(file_entry, None)

  def testGetFileEntryByPathSpec(self):
    """Test the get entry by path specification functionality."""
    path_spec = tsk_path_spec.TSKPathSpec(inode=15, parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)

  def testGetLinkedFileEntry(self):
    """Test the get linked file entry functionality."""
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=13, location=u'/a_link', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)

    linked_file_entry = file_entry.GetLinkedFileEntry()

    self.assertNotEquals(linked_file_entry, None)

    self.assertEquals(linked_file_entry.name, u'another_file')

  def testGetParentFileEntry(self):
    """Test the get parent file entry functionality."""
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=16, location=u'/a_directory/another_file',
        parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertNotEquals(parent_file_entry, None)

    self.assertEquals(parent_file_entry.name, u'a_directory')

  def testGetStat(self):
    """Test the get stat functionality."""
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=16, location=u'/a_directory/another_file',
        parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    stat_object = file_entry.GetStat()

    self.assertNotEquals(stat_object, None)
    self.assertEquals(stat_object.type, stat_object.TYPE_FILE)

  def testIsFunctions(self):
    """Test the Is? functionality."""
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=16, location=u'/a_directory/another_file',
        parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertFalse(file_entry.IsRoot())
    self.assertFalse(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertFalse(file_entry.IsDirectory())
    self.assertTrue(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

    path_spec = tsk_path_spec.TSKPathSpec(
        inode=12, location=u'/a_directory',
        parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertFalse(file_entry.IsRoot())
    self.assertFalse(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertTrue(file_entry.IsDirectory())
    self.assertFalse(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

    path_spec = tsk_path_spec.TSKPathSpec(
        location=u'/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertTrue(file_entry.IsRoot())
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
    path_spec = tsk_path_spec.TSKPathSpec(
        location=u'/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)

    self.assertEquals(file_entry.number_of_sub_file_entries, 5)

    # Note that passwords.txt~ is currently ignored by dfvfs, since
    # its directory entry has no pytsk3.TSK_FS_META object.
    expected_sub_file_entry_names = [
        u'a_directory',
        u'a_link',
        u'lost+found',
        u'passwords.txt',
        u'$OrphanFiles' ]

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEquals(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEquals(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))


if __name__ == '__main__':
  unittest.main()
