#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the attribute implementation using pytsk3."""

import unittest

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import tsk_attribute
from dfvfs.vfs import tsk_file_system

from tests import test_lib as shared_test_lib


class TSKAttributeTest(shared_test_lib.BaseTestCase):
  """Tests the TSK attribute."""

  # pylint: disable=protected-access

  _INODE_A_FILE = 19

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['hfsplus.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._tsk_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/',
        parent=self._raw_path_spec)

    self._file_system = tsk_file_system.TSKFileSystem(
        self._resolver_context, self._tsk_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testIntialize(self):
    """Tests the __init__ function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_FILE,
        location='/a_directory/a_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    pytsk_attribute = next(file_entry._tsk_file)
    self.assertIsNotNone(pytsk_attribute)

    test_attribute = tsk_attribute.TSKAttribute(
        file_entry._tsk_file, pytsk_attribute)
    self.assertIsNotNone(test_attribute)

    with self.assertRaises(errors.BackEndError):
      tsk_attribute.TSKAttribute(None, pytsk_attribute)

    with self.assertRaises(errors.BackEndError):
      tsk_attribute.TSKAttribute(file_entry._tsk_file, None)


class TSKExtendedAttributeTest(shared_test_lib.BaseTestCase):
  """Tests the TSK extended attribute."""

  # pylint: disable=protected-access

  _INODE_A_FILE = 19

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['hfsplus.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._tsk_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/',
        parent=self._raw_path_spec)

    self._file_system = tsk_file_system.TSKFileSystem(
        self._resolver_context, self._tsk_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testIntialize(self):
    """Tests the __init__ function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._INODE_A_FILE,
        location='/a_directory/a_file', parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    pytsk_attribute = next(file_entry._tsk_file)
    self.assertIsNotNone(pytsk_attribute)
    self.assertEqual(pytsk_attribute.info.name, b'myxattr')

    test_attribute = tsk_attribute.TSKExtendedAttribute(
        file_entry._tsk_file, pytsk_attribute)
    self.assertIsNotNone(test_attribute)


if __name__ == '__main__':
  unittest.main()
