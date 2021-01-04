#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Extended File System (EXT) file-like object."""

import os
import unittest

from dfvfs.file_io import ext_file_io
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context

from tests import test_lib as shared_test_lib


class EXTFileTest(shared_test_lib.BaseTestCase):
  """Tests the file-like object implementation using pyfsext.file_entry."""

  _IDENTIFIER_ANOTHER_FILE = 15
  _IDENTIFIER_PASSWORDS_TXT = 14

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(EXTFileTest, self).setUp()
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['ext2.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenCloseIdentifier(self):
    """Test the open and close functionality using an inode."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT,
        inode=self._IDENTIFIER_PASSWORDS_TXT,
        parent=self._raw_path_spec)
    file_object = ext_file_io.EXTFile(self._resolver_context, path_spec)

    file_object.Open()
    self.assertEqual(file_object.get_size(), 116)

    # TODO: add a failing scenario.

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, location='/passwords.txt',
        parent=self._raw_path_spec)
    file_object = ext_file_io.EXTFile(self._resolver_context, path_spec)

    file_object.Open()
    self.assertEqual(file_object.get_size(), 116)

    # Try open with a path specification that has no parent.
    path_spec.parent = None
    file_object = ext_file_io.EXTFile(self._resolver_context, path_spec)

    with self.assertRaises(errors.PathSpecError):
      file_object.Open()

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, location='/a_directory/another_file',
        inode=self._IDENTIFIER_ANOTHER_FILE,
        parent=self._raw_path_spec)
    file_object = ext_file_io.EXTFile(self._resolver_context, path_spec)

    file_object.Open()
    self.assertEqual(file_object.get_size(), 22)

    file_object.seek(10)
    self.assertEqual(file_object.read(5), b'other')
    self.assertEqual(file_object.get_offset(), 15)

    file_object.seek(-10, os.SEEK_END)
    self.assertEqual(file_object.read(5), b'her f')

    file_object.seek(2, os.SEEK_CUR)
    self.assertEqual(file_object.read(2), b'e.')

    # Conforming to the POSIX seek the offset can exceed the file size
    # but reading will result in no data being returned.
    file_object.seek(300, os.SEEK_SET)
    self.assertEqual(file_object.get_offset(), 300)
    self.assertEqual(file_object.read(2), b'')

    with self.assertRaises(IOError):
      file_object.seek(-10, os.SEEK_SET)

    # On error the offset should not change.
    self.assertEqual(file_object.get_offset(), 300)

    with self.assertRaises(IOError):
      file_object.seek(10, 5)

    # On error the offset should not change.
    self.assertEqual(file_object.get_offset(), 300)

  def testRead(self):
    """Test the read functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, location='/passwords.txt',
        inode=self._IDENTIFIER_PASSWORDS_TXT,
        parent=self._raw_path_spec)
    file_object = ext_file_io.EXTFile(self._resolver_context, path_spec)

    file_object.Open()
    read_buffer = file_object.read()

    expected_buffer = (
        b'place,user,password\n'
        b'bank,joesmith,superrich\n'
        b'alarm system,-,1234\n'
        b'treasure chest,-,1111\n'
        b'uber secret laire,admin,admin\n')

    self.assertEqual(read_buffer, expected_buffer)

    # TODO: add boundary scenarios.


if __name__ == '__main__':
  unittest.main()
