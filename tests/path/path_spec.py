#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Virtual File System (VFS) path specification interface."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import path_spec

from tests.path import test_lib


class TestPathSpec(path_spec.PathSpec):
  """Path specification for testing."""

  TYPE_INDICATOR = 'test'

  def __init__(self, parent=None, **kwargs):
    """Initializes a path specification.

    Args:
      parent (Optional[PathSpec]): parent path specification.
    """
    super(TestPathSpec, self).__init__(parent=parent, **kwargs)
    self.attribute = 'MyAttribute'


class PathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the VFS path specification interface."""

  # pylint: disable=protected-access

  def testInitialize(self):
    """Tests the __init__ function."""
    with self.assertRaises(ValueError):
      path_spec.PathSpec()

  # TODO: add tests for __eq__
  # TODO: add tests for __hash__

  def testGetComparable(self):
    """Tests the _GetComparable function."""
    test_path_spec = TestPathSpec()

    test_comparable = test_path_spec._GetComparable()
    self.assertEqual(test_comparable, 'type: test\n')

  def testComparable(self):
    """Tests the comparable property."""
    test_path_spec = TestPathSpec()

    self.assertEqual(test_path_spec.comparable, 'type: test\n')

  def testTypeIndicator(self):
    """Tests the type_indicator property."""
    test_path_spec = TestPathSpec()

    self.assertEqual(test_path_spec.type_indicator, 'test')

  def testCopyToDict(self):
    """Tests the CopyToDict function."""
    test_path_spec = TestPathSpec()

    test_dict = test_path_spec.CopyToDict()
    self.assertEqual(test_dict, {'attribute': 'MyAttribute'})

  def testHasParent(self):
    """Tests the HasParent function."""
    test_path_spec = TestPathSpec()

    self.assertFalse(test_path_spec.HasParent())

  def testIsFileSystem(self):
    """Tests the IsFileSystem function."""
    test_path_spec = TestPathSpec()

    self.assertFalse(test_path_spec.IsFileSystem())

  def testIsSystemLevel(self):
    """Tests the IsSystemLevel function."""
    test_path_spec = TestPathSpec()

    self.assertFalse(test_path_spec.IsSystemLevel())

  def testIsVolumeSystem(self):
    """Tests the IsVolumeSystem function."""
    test_path_spec = TestPathSpec()

    self.assertFalse(test_path_spec.IsVolumeSystem())

  def testIsVolumeSystemRoot(self):
    """Tests the IsVolumeSystemRoot function."""
    test_path_spec = TestPathSpec()

    self.assertFalse(test_path_spec.IsVolumeSystemRoot())


if __name__ == '__main__':
  unittest.main()
