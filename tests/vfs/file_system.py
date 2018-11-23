#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the VFS file system object interface."""

from __future__ import unicode_literals

import unittest

from dfvfs.resolver import context
from dfvfs.vfs import file_system

from tests import test_lib as shared_test_lib


class TestFileSystem(file_system.FileSystem):
  """File system for testing."""

  # pylint: disable=abstract-method

  TYPE_INDICATOR = 'test'


class FileSystemTest(shared_test_lib.BaseTestCase):
  """Tests the VFS file system object interface."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def testIntialize(self):
    """Test the __init__ function."""
    with self.assertRaises(ValueError):
      file_system.FileSystem(self._resolver_context)

  # TODO: add tests for type_indicator property.
  # TODO: add tests for _Close function.
  # TODO: add tests for _Open function.
  # TODO: add tests for BasenamePath function.
  # TODO: add tests for Close function.
  # TODO: add tests for DirnamePath function.
  # TODO: add tests for GetDataStreamByPathSpec function.
  # TODO: add tests for GetFileObjectByPathSpec function.
  # TODO: add tests for GetPathSegmentAndSuffix function.

  def testJoinPath(self):
    """Test the join path functionality."""
    test_file_system = TestFileSystem(self._resolver_context)

    expected_path = '/test1/test2/test3'

    path = test_file_system.JoinPath(['test1', 'test2', 'test3'])
    self.assertEqual(path, expected_path)

    path = test_file_system.JoinPath(['/test1', 'test2//', 'test3/'])
    self.assertEqual(path, expected_path)

    path = test_file_system.JoinPath(['/test1/test2/', '/test3/'])
    self.assertEqual(path, expected_path)

    path = test_file_system.JoinPath(['/test1///test2', 'test3'])
    self.assertEqual(path, expected_path)

  # TODO: add tests for Open function.

  def testSplitPath(self):
    """Test the split path functionality."""
    test_file_system = TestFileSystem(self._resolver_context)

    expected_path_segments = ['test1', 'test2', 'test3']

    path_segments = test_file_system.SplitPath('/test1/test2/test3')
    self.assertEqual(path_segments, expected_path_segments)

    path_segments = test_file_system.SplitPath('/test1/test2/test3/')
    self.assertEqual(path_segments, expected_path_segments)

    path_segments = test_file_system.SplitPath('/test1///test2/test3')
    self.assertEqual(path_segments, expected_path_segments)


if __name__ == '__main__':
  unittest.main()
