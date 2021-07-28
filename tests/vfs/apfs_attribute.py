#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the APFS attribute."""

import unittest

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import apfs_attribute
from dfvfs.vfs import apfs_file_system

from tests import test_lib as shared_test_lib


class APFSExtendedAttributeTest(shared_test_lib.BaseTestCase):
  """Tests the APFS extended attribute."""

  # pylint: disable=protected-access

  _IDENTIFIER_A_FILE = 17

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['apfs.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._apfs_container_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, location='/apfs1',
        parent=test_raw_path_spec)
    self._apfs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS, location='/',
        parent=self._apfs_container_path_spec)

    self._file_system = apfs_file_system.APFSFileSystem(
        self._resolver_context, self._apfs_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testIntialize(self):
    """Tests the __init__ function."""
    test_location = '/a_directory/a_file'
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS, identifier=self._IDENTIFIER_A_FILE,
        location=test_location, parent=self._apfs_container_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    fsapfs_attribute = file_entry._fsapfs_file_entry.get_extended_attribute(0)
    self.assertIsNotNone(fsapfs_attribute)
    self.assertEqual(fsapfs_attribute.name, 'myxattr')

    test_attribute = apfs_attribute.APFSExtendedAttribute(fsapfs_attribute)
    self.assertIsNotNone(test_attribute)

    with self.assertRaises(errors.BackEndError):
      apfs_attribute.APFSExtendedAttribute(None)


if __name__ == '__main__':
  unittest.main()
