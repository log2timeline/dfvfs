#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The dfVFS Project Authors.
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
"""Tests for the file system implementation using os."""

import os
import platform
import unittest

from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import os_file_system


class OSFileSystemTest(unittest.TestCase):
  """The unit test for the operating system file system object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def testIntialize(self):
    """Test the intialize functionality."""
    file_system = os_file_system.OSFileSystem(self._resolver_context)

    self.assertNotEquals(file_system, None)

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = os_file_system.OSFileSystem(self._resolver_context)

    path_spec = os_path_spec.OSPathSpec(
        location=os.path.join('test_data', 'testdir_os', 'file1.txt'))
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = os_path_spec.OSPathSpec(
        location=os.path.join('test_data', 'testdir_os', 'file6.txt'))
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

  def testGetFileEntryByPathSpec(self):
    """Test the get entry by path specification functionality."""
    file_system = os_file_system.OSFileSystem(self._resolver_context)

    path_spec = os_path_spec.OSPathSpec(
        location=os.path.join('test_data', 'testdir_os', 'file1.txt'))
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)
    self.assertEquals(file_entry.name, u'file1.txt')

    path_spec = os_path_spec.OSPathSpec(
        location=os.path.join('test_data', 'testdir_os', 'file6.txt'))
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertEquals(file_entry, None)

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = os_file_system.OSFileSystem(self._resolver_context)

    if platform.system() == 'Windows':
      # Return the root with the drive letter of the volume the current
      # working directory is on.
      expected_location = os.getcwd()
      expected_location, _, _ = expected_location.partition('\\')
    else:
      expected_location = u''

    file_entry = file_system.GetRootFileEntry()

    self.assertNotEquals(file_entry, None)
    self.assertEquals(file_entry.name, expected_location)


if __name__ == '__main__':
  unittest.main()
