#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The PyVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for the file entry implementation using the SleuthKit (TSK)."""

import os
import unittest

from pyvfs.file_io import os_file_io
from pyvfs.path import os_path_spec
from pyvfs.path import tsk_path_spec
from pyvfs.vfs import tsk_file_entry
from pyvfs.vfs import tsk_file_system


class TSKFileEntryTest(unittest.TestCase):
  """The unit test for the SleuthKit (TSK) file entry object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = os.path.join('test_data', 'image.dd')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._os_file_object = os_file_io.OSFile()
    self._os_file_object.open(self._os_path_spec, mode='rb')
    self._tsk_file_system = tsk_file_system.TSKFileSystem(
        self._os_file_object, self._os_path_spec)

  def testIntialize(self):
    """Test the initialize functionality."""
    file_entry = tsk_file_entry.TSKFileEntry(
        self._os_file_object, self._os_path_spec)

    self.assertNotEquals(file_entry, None)

  def testGetFileEntryByPathSpec(self):
    """Test the get entry by path specification functionality."""
    path_spec = tsk_path_spec.TSKPathSpec(inode=15, parent=self._os_path_spec)
    file_entry = self._tsk_file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)

  def testGetParentFileEntry(self):
    """Test the get parent file entry functionality."""
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=16, location=u'/a_directory/another_file',
        parent=self._os_path_spec)
    file_entry = self._tsk_file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertNotEquals(parent_file_entry, None)

    self.assertEquals(parent_file_entry.name, u'a_directory')

  def testSubFileEntries(self):
    """Test the sub file entries iteration functionality."""
    path_spec = tsk_path_spec.TSKPathSpec(
        location=u'/', parent=self._os_path_spec)
    file_entry = self._tsk_file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)

    # Note that passwords.txt~ is currently ignored by pyvfs, since
    # its directory entry has no pytsk3.TSK_FS_META object.
    expected_sub_file_entry_names = [
        u'a_directory',
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
