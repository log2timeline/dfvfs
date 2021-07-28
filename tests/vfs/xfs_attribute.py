#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the XFS attribute."""

import unittest

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import xfs_attribute
from dfvfs.vfs import xfs_file_system

from tests import test_lib as shared_test_lib


class XFSExtendedAttributeTest(shared_test_lib.BaseTestCase):
  """Tests the XFS extended attribute."""

  # pylint: disable=protected-access

  _INODE_A_FILE = 11076

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['xfs.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._xfs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, location='/',
        parent=self._raw_path_spec)

    self._file_system = xfs_file_system.XFSFileSystem(
        self._resolver_context, self._xfs_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testIntialize(self):
    """Tests the __init__ function."""
    test_location = '/a_directory/a_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, inode=self._INODE_A_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    fsxfs_attribute = file_entry._fsxfs_file_entry.get_extended_attribute(1)
    self.assertIsNotNone(fsxfs_attribute)
    self.assertEqual(fsxfs_attribute.name, 'user.myxattr')

    test_attribute = xfs_attribute.XFSExtendedAttribute(fsxfs_attribute)
    self.assertIsNotNone(test_attribute)

    with self.assertRaises(errors.BackEndError):
      xfs_attribute.XFSExtendedAttribute(None)


if __name__ == '__main__':
  unittest.main()
