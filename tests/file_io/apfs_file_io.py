#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Apple File System (APFS) file-like object."""

from __future__ import unicode_literals

import os
import unittest

from dfvfs.file_io import apfs_file_io
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context

from tests.file_io import test_lib


class APFSFileTest(test_lib.ImageFileTestCase):
  """Tests the file-like object implementation using pyfsapfs.file_entry."""

  _IDENTIFIER_ANOTHER_FILE = 21
  _IDENTIFIER_PASSWORDS_TXT = 19

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(APFSFileTest, self).setUp()
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['apfs.dmg'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    test_tsk_partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/p1',
        parent=test_raw_path_spec)
    self._apfs_container_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, location='/apfs1',
        parent=test_tsk_partition_path_spec)

  def testOpenCloseIdentifier(self):
    """Test the open and close functionality using an identifier."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS,
        identifier=self._IDENTIFIER_PASSWORDS_TXT,
        parent=self._apfs_container_path_spec)
    file_object = apfs_file_io.APFSFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 116)
    file_object.close()

    # TODO: add a failing scenario.

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS, location='/passwords.txt',
        parent=self._apfs_container_path_spec)
    file_object = apfs_file_io.APFSFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 116)
    file_object.close()

    # Try open with a path specification that has no parent.
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS, location='/a_directory/another_file',
        identifier=self._IDENTIFIER_ANOTHER_FILE,
        parent=self._apfs_container_path_spec)
    file_object = apfs_file_io.APFSFile(self._resolver_context)

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
        definitions.TYPE_INDICATOR_APFS, location='/passwords.txt',
        identifier=self._IDENTIFIER_PASSWORDS_TXT,
        parent=self._apfs_container_path_spec)
    file_object = apfs_file_io.APFSFile(self._resolver_context)

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
