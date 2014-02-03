#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 The dfVFS Project Authors.
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
"""Tests for the fake file entry implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import fake_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import fake_file_entry
from dfvfs.vfs import fake_file_system


class FakeFileEntryTest(unittest.TestCase):
  """The unit test for the fake file entry object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    self._fake_file_system = fake_file_system.FakeFileSystem(
        self._resolver_context)
    self._fake_file_system.AddFileEntry(
        u'/test_data/testdir_fake',
        file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)
    self._fake_file_system.AddFileEntry(
        u'/test_data/testdir_fake/file1.txt', file_data='FILE1')
    self._fake_file_system.AddFileEntry(
        u'/test_data/testdir_fake/file2.txt', file_data='FILE2')
    self._fake_file_system.AddFileEntry(
        u'/test_data/testdir_fake/file3.txt', file_data='FILE3')
    self._fake_file_system.AddFileEntry(
        u'/test_data/testdir_fake/file4.txt', file_data='FILE4')
    self._fake_file_system.AddFileEntry(
        u'/test_data/testdir_fake/file5.txt', file_data='FILE5')

    self._test_file = u'/test_data/testdir_fake'

  def testIntialize(self):
    """Test the initialize functionality."""
    path_spec = fake_path_spec.FakePathSpec(location=self._test_file)
    file_entry = fake_file_entry.FakeFileEntry(
        self._resolver_context, self._fake_file_system, path_spec)

    self.assertNotEquals(file_entry, None)

  def testGetFileEntryByPathSpec(self):
    """Test the get a file entry by path specification functionality."""
    path_spec = fake_path_spec.FakePathSpec(location=self._test_file)
    file_entry = self._fake_file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)

  def testGetParentFileEntry(self):
    """Test the get parent file entry functionality."""
    test_file = u'/test_data/testdir_fake/file1.txt'
    path_spec = fake_path_spec.FakePathSpec(location=test_file)
    file_entry = self._fake_file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertNotEquals(parent_file_entry, None)

    self.assertEquals(parent_file_entry.name, u'testdir_fake')

  def testGetStat(self):
    """Test the get stat functionality."""
    test_file = u'/test_data/testdir_fake/file1.txt'
    path_spec = fake_path_spec.FakePathSpec(location=test_file)
    file_entry = self._fake_file_system.GetFileEntryByPathSpec(path_spec)

    stat_object = file_entry.GetStat()

    self.assertNotEquals(stat_object, None)
    self.assertEquals(stat_object.type, stat_object.TYPE_FILE)

  def testIsFunctions(self):
    """Test the Is? functionality."""
    test_file = u'/test_data/testdir_fake/file1.txt'
    path_spec = fake_path_spec.FakePathSpec(location=test_file)
    file_entry = self._fake_file_system.GetFileEntryByPathSpec(path_spec)

    self.assertFalse(file_entry.IsRoot())
    self.assertTrue(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertFalse(file_entry.IsDirectory())
    self.assertTrue(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

    test_file = u'/test_data/testdir_fake'
    path_spec = fake_path_spec.FakePathSpec(location=test_file)
    file_entry = self._fake_file_system.GetFileEntryByPathSpec(path_spec)

    self.assertFalse(file_entry.IsRoot())
    self.assertTrue(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertTrue(file_entry.IsDirectory())
    self.assertFalse(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

  def testSubFileEntries(self):
    """Test the sub file entries iteration functionality."""
    path_spec = fake_path_spec.FakePathSpec(location=self._test_file)
    file_entry = self._fake_file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)

    expected_sub_file_entry_names = [
        u'file1.txt', u'file2.txt', u'file3.txt', u'file4.txt', u'file5.txt']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEquals(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEquals(
        sorted(sub_file_entry_names), expected_sub_file_entry_names)


if __name__ == '__main__':
  unittest.main()
