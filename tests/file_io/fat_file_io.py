#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the File Allocation Table (FAT) file-like object."""

import unittest

from dfvfs.file_io import fat_file_io
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context

from tests.file_io import test_lib


class FATFileTest(test_lib.FAT12ImageFileTestCase):
  """Tests the file-like object implementation using pyfsfat.file_entry."""

  _IDENTIFIER_ANOTHER_FILE = 0x62a0
  _IDENTIFIER_PASSWORDS_TXT = 0x1a80

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(FATFileTest, self).setUp()
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['fat12.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenCloseIdentifier(self):
    """Test the open and close functionality using an identifier."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_FAT,
        identifier=self._IDENTIFIER_PASSWORDS_TXT, parent=self._raw_path_spec)
    file_object = fat_file_io.FATFile(self._resolver_context, path_spec)

    self._TestOpenCloseIdentifier(file_object)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_FAT,
        identifier=self._IDENTIFIER_PASSWORDS_TXT, location='\\passwords.txt',
        parent=self._raw_path_spec)
    file_object = fat_file_io.FATFile(self._resolver_context, path_spec)

    self._TestOpenCloseLocation(file_object)

    # Try open with a path specification that has no parent.
    path_spec.parent = None
    file_object = fat_file_io.FATFile(self._resolver_context, path_spec)

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_FAT, location='\\a_directory\\another_file',
        identifier=self._IDENTIFIER_ANOTHER_FILE,
        parent=self._raw_path_spec)
    file_object = fat_file_io.FATFile(self._resolver_context, path_spec)

    self._TestSeek(file_object)

  def testRead(self):
    """Test the read functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_FAT, location='\\passwords.txt',
        identifier=self._IDENTIFIER_PASSWORDS_TXT,
        parent=self._raw_path_spec)
    file_object = fat_file_io.FATFile(self._resolver_context, path_spec)

    self._TestRead(file_object)


if __name__ == '__main__':
  unittest.main()
