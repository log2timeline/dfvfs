#!/usr/bin/python
# -*- coding: utf-8 -*-
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

    self.assertIsNotNone(test_file_system)

  def testJoinPath(self):
    """Test the join path functionality."""
    test_file_system = file_system.FileSystem(self._resolver_context)

    expected_path = u'/test1/test2/test3'

    path = test_file_system.JoinPath([u'test1', u'test2', u'test3'])
    self.assertEqual(path, expected_path)

    path = test_file_system.JoinPath([u'/test1', u'test2//', u'test3/'])
    self.assertEqual(path, expected_path)

    path = test_file_system.JoinPath([u'/test1/test2/', u'/test3/'])
    self.assertEqual(path, expected_path)

    path = test_file_system.JoinPath([u'/test1///test2', u'test3'])
    self.assertEqual(path, expected_path)

  def testSplitPath(self):
    """Test the split path functionality."""
    test_file_system = file_system.FileSystem(self._resolver_context)

    expected_path_segments = [u'test1', u'test2', u'test3']

    path_segments = test_file_system.SplitPath(u'/test1/test2/test3')
    self.assertEqual(path_segments, expected_path_segments)

    path_segments = test_file_system.SplitPath(u'/test1/test2/test3/')
    self.assertEqual(path_segments, expected_path_segments)

    path_segments = test_file_system.SplitPath(u'/test1///test2/test3')
    self.assertEqual(path_segments, expected_path_segments)


if __name__ == '__main__':
  unittest.main()
