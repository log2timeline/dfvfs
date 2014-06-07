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
"""Tests for the fake file system implementation."""

import unittest

from dfvfs.path import fake_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import fake_file_system


class FakeFileSystemTest(unittest.TestCase):
  """The unit test for the fake file system object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def testIntialize(self):
    """Test the intialize functionality."""
    file_system = fake_file_system.FakeFileSystem(self._resolver_context)

    self.assertNotEquals(file_system, None)

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = fake_file_system.FakeFileSystem(self._resolver_context)
    file_system.AddFileEntry(
        u'/test_data/testdir_fake/file1.txt', file_data='FILE1')

    path_spec = fake_path_spec.FakePathSpec(
        location=u'/test_data/testdir_fake/file1.txt')
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = fake_path_spec.FakePathSpec(
        location=u'/test_data/testdir_fake/file6.txt')
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

  def testGetFileEntryByPathSpec(self):
    """Test the get entry by path specification functionality."""
    file_system = fake_file_system.FakeFileSystem(self._resolver_context)
    file_system.AddFileEntry(
        u'/test_data/testdir_fake/file1.txt', file_data='FILE1')

    path_spec = fake_path_spec.FakePathSpec(
        location=u'/test_data/testdir_fake/file1.txt')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)
    self.assertEquals(file_entry.name, u'file1.txt')

    path_spec = fake_path_spec.FakePathSpec(
        location=u'/test_data/testdir_fake/file6.txt')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertEquals(file_entry, None)

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = fake_file_system.FakeFileSystem(self._resolver_context)

    file_entry = file_system.GetRootFileEntry()

    self.assertNotEquals(file_entry, None)
    self.assertEquals(file_entry.name, u'')


if __name__ == '__main__':
  unittest.main()
