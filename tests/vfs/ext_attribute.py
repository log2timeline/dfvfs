#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the EXT attribute."""

import unittest

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import ext_attribute
from dfvfs.vfs import ext_file_system

from tests import test_lib as shared_test_lib


class EXTExtendedAttributeTest(shared_test_lib.BaseTestCase):
  """Tests the EXT extended attribute."""

  # pylint: disable=protected-access

  _INODE_A_FILE = 13

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['ext2.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, location='/',
        parent=self._raw_path_spec)

    self._file_system = ext_file_system.EXTFileSystem(
        self._resolver_context, self._ext_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testIntialize(self):
    """Tests the __init__ function."""
    test_location = '/a_directory/a_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, inode=self._INODE_A_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    fsext_attribute = file_entry._fsext_file_entry.get_extended_attribute(0)
    self.assertIsNotNone(fsext_attribute)
    self.assertEqual(fsext_attribute.name, 'user.myxattr')

    test_attribute = ext_attribute.EXTExtendedAttribute(fsext_attribute)
    self.assertIsNotNone(test_attribute)

    with self.assertRaises(errors.BackEndError):
      ext_attribute.EXTExtendedAttribute(None)


if __name__ == '__main__':
  unittest.main()
