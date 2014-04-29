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
"""Tests for the VFS file system object interface."""

import unittest

from dfvfs.resolver import context
from dfvfs.vfs import file_system


class FileSystemTest(unittest.TestCase):
  """The unit test for the VFS file system object interface."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def testIntialize(self):
    """Test the intialize functionality."""
    test_file_system = file_system.FileSystem(self._resolver_context)

    self.assertNotEquals(test_file_system, None)

  def testJoinPath(self):
    """Test the join path functionality."""
    test_file_system = file_system.FileSystem(self._resolver_context)

    expected_path = u'/test1/test2/test3'

    path = test_file_system.JoinPath([u'test1', u'test2', u'test3'])
    self.assertEquals(path, expected_path)

    path = test_file_system.JoinPath([u'/test1', u'test2//', u'test3/'])
    self.assertEquals(path, expected_path)

    path = test_file_system.JoinPath([u'/test1/test2/', u'/test3/'])
    self.assertEquals(path, expected_path)

    path = test_file_system.JoinPath([u'/test1///test2', u'test3'])
    self.assertEquals(path, expected_path)

  def testSplitPath(self):
    """Test the split path functionality."""
    test_file_system = file_system.FileSystem(self._resolver_context)

    expected_path_segments = [u'test1', u'test2', u'test3']

    path_segments = test_file_system.SplitPath(u'/test1/test2/test3')
    self.assertEquals(path_segments, expected_path_segments)

    path_segments = test_file_system.SplitPath(u'/test1/test2/test3/')
    self.assertEquals(path_segments, expected_path_segments)

    path_segments = test_file_system.SplitPath(u'/test1///test2/test3')
    self.assertEquals(path_segments, expected_path_segments)


if __name__ == '__main__':
  unittest.main()
