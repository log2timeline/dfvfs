#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the attribute implementation using pyfsntfs."""

import unittest

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import ntfs_attribute
from dfvfs.vfs import ntfs_file_system

from tests import test_lib as shared_test_lib


class TestNTFSAttribute(ntfs_attribute.NTFSAttribute):
  """NTFS attribute for testing."""

  # pylint: disable=abstract-method

  TYPE_INDICATOR = 'test'


class NTFSAttributeTest(shared_test_lib.BaseTestCase):
  """Tests the NTFS attribute."""

  # pylint: disable=protected-access

  _MFT_ENTRY_PASSWORDS_TXT = 66

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['ntfs.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._ntfs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\',
        parent=self._raw_path_spec)

    self._file_system = ntfs_file_system.NTFSFileSystem(
        self._resolver_context, self._ntfs_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testIntialize(self):
    """Tests the __init__ function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, mft_attribute=1,
        mft_entry=self._MFT_ENTRY_PASSWORDS_TXT, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    fsntfs_attribute = file_entry._fsntfs_file_entry.get_attribute(0)
    test_attribute = TestNTFSAttribute(fsntfs_attribute)
    self.assertIsNotNone(test_attribute)

    with self.assertRaises(errors.BackEndError):
      TestNTFSAttribute(None)

  def testAttributeType(self):
    """Test the attribute_type property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, mft_attribute=1,
        mft_entry=self._MFT_ENTRY_PASSWORDS_TXT, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    fsntfs_attribute = file_entry._fsntfs_file_entry.get_attribute(0)
    test_attribute = TestNTFSAttribute(fsntfs_attribute)

    self.assertEqual(test_attribute.attribute_type, 0x00000010)


class FileNameNTFSAttributeTest(shared_test_lib.BaseTestCase):
  """Tests the NTFS $FILE_NAME attribute."""

  # pylint: disable=protected-access

  _MFT_ENTRY_PASSWORDS_TXT = 66

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['ntfs.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._ntfs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\',
        parent=self._raw_path_spec)

    self._file_system = ntfs_file_system.NTFSFileSystem(
        self._resolver_context, self._ntfs_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testIntialize(self):
    """Tests the __init__ function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, mft_attribute=1,
        mft_entry=self._MFT_ENTRY_PASSWORDS_TXT, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    fsntfs_attribute = file_entry._fsntfs_file_entry.get_attribute(1)
    test_attribute = ntfs_attribute.FileNameNTFSAttribute(fsntfs_attribute)
    self.assertIsNotNone(test_attribute)

    with self.assertRaises(errors.BackEndError):
      ntfs_attribute.FileNameNTFSAttribute(None)

  def testAttributeType(self):
    """Test the attribute_type property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, mft_attribute=1,
        mft_entry=self._MFT_ENTRY_PASSWORDS_TXT, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    fsntfs_attribute = file_entry._fsntfs_file_entry.get_attribute(1)
    test_attribute = ntfs_attribute.FileNameNTFSAttribute(fsntfs_attribute)

    self.assertEqual(test_attribute.attribute_type, 0x00000030)


# TODO: add tests for ObjectIdentifierNTFSAttribute.
# TODO: add tests for SecurityDescriptorNTFSAttribute.


class StandardInformationNTFSAttributeTest(shared_test_lib.BaseTestCase):
  """Tests the NTFS $STANDARD_INFORMATION attribute."""

  # pylint: disable=protected-access

  _MFT_ENTRY_PASSWORDS_TXT = 66

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['ntfs.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._ntfs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\',
        parent=self._raw_path_spec)

    self._file_system = ntfs_file_system.NTFSFileSystem(
        self._resolver_context, self._ntfs_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testIntialize(self):
    """Tests the __init__ function."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, mft_attribute=1,
        mft_entry=self._MFT_ENTRY_PASSWORDS_TXT, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    fsntfs_attribute = file_entry._fsntfs_file_entry.get_attribute(0)
    test_attribute = ntfs_attribute.StandardInformationNTFSAttribute(
        fsntfs_attribute)
    self.assertIsNotNone(test_attribute)

    with self.assertRaises(errors.BackEndError):
      ntfs_attribute.StandardInformationNTFSAttribute(None)

  def testAttributeType(self):
    """Test the attribute_type property."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, mft_attribute=1,
        mft_entry=self._MFT_ENTRY_PASSWORDS_TXT, parent=self._raw_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    fsntfs_attribute = file_entry._fsntfs_file_entry.get_attribute(0)
    test_attribute = ntfs_attribute.StandardInformationNTFSAttribute(
        fsntfs_attribute)

    self.assertEqual(test_attribute.attribute_type, 0x00000010)


if __name__ == '__main__':
  unittest.main()
