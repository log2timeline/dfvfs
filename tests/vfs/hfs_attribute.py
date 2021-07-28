#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the HFS attribute."""

import unittest

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import hfs_attribute
from dfvfs.vfs import hfs_file_system

from tests import test_lib as shared_test_lib


class HFSExtendedAttributeTest(shared_test_lib.BaseTestCase):
  """Tests the HFS extended attribute."""

  # pylint: disable=protected-access

  _IDENTIFIER_A_FILE = 19

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['hfsplus.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._hfs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS, location='/',
        parent=self._raw_path_spec)

    self._file_system = hfs_file_system.HFSFileSystem(
        self._resolver_context, self._hfs_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testIntialize(self):
    """Tests the __init__ function."""
    test_location = '/a_directory/a_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS, identifier=self._IDENTIFIER_A_FILE,
        location=test_location, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    fshfs_attribute = file_entry._fshfs_file_entry.get_extended_attribute(0)
    self.assertIsNotNone(fshfs_attribute)
    self.assertEqual(fshfs_attribute.name, 'myxattr')

    test_attribute = hfs_attribute.HFSExtendedAttribute(fshfs_attribute)
    self.assertIsNotNone(test_attribute)

    with self.assertRaises(errors.BackEndError):
      hfs_attribute.HFSExtendedAttribute(None)


if __name__ == '__main__':
  unittest.main()
