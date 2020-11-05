#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Extended File System (HFS) file-like object."""

from __future__ import unicode_literals

import os
import unittest

from dfvfs.file_io import hfs_file_io
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context

from tests import test_lib as shared_test_lib


class HFSFileTest(shared_test_lib.BaseTestCase):
  """Tests the file-like object implementation using pyfshfs.file_entry."""

  _IDENTIFIER_ANOTHER_FILE = 21
  _IDENTIFIER_PASSWORDS_TXT = 20

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(HFSFileTest, self).setUp()
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['hfsplus.raw'])
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
        definitions.TYPE_INDICATOR_HFS,
        identifier=self._IDENTIFIER_PASSWORDS_TXT,
        parent=self._raw_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 116)
    file_object.close()

    # TODO: add a failing scenario.

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS, location='/passwords.txt',
        parent=self._raw_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 116)
    file_object.close()

    # Try open with a path specification that has no parent.
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS, location='/a_directory/another_file',
        identifier=self._IDENTIFIER_ANOTHER_FILE,
        parent=self._raw_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
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

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS, location='/passwords.txt',
        identifier=self._IDENTIFIER_PASSWORDS_TXT,
        parent=self._raw_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    read_buffer = file_object.read()

    expected_buffer = (
        b'place,user,password\n'
        b'bank,joesmith,superrich\n'
        b'alarm system,-,1234\n'
        b'treasure chest,-,1111\n'
        b'uber secret laire,admin,admin\n')

    self.assertEqual(read_buffer, expected_buffer)

    # TODO: add boundary scenarios.

    file_object.close()


if __name__ == '__main__':
  unittest.main()
