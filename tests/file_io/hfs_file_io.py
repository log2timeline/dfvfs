#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Hierarchical File System (HFS) file-like object."""

import unittest

from dfvfs.file_io import hfs_file_io
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context

from tests.file_io import test_lib


class HFSFileTest(test_lib.HFSImageFileTestCase):
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
        identifier=self._IDENTIFIER_PASSWORDS_TXT, parent=self._raw_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestOpenCloseIdentifier(file_object)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS,
        identifier=self._IDENTIFIER_PASSWORDS_TXT, location='/passwords.txt',
        parent=self._raw_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestOpenCloseLocation(file_object)

    # Try open with a path specification that has no parent.
    path_spec.parent = None
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS, location='/a_directory/another_file',
        identifier=self._IDENTIFIER_ANOTHER_FILE,
        parent=self._raw_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestSeek(file_object)

  def testRead(self):
    """Test the read functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS, location='/passwords.txt',
        identifier=self._IDENTIFIER_PASSWORDS_TXT,
        parent=self._raw_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestRead(file_object)

  def testReadResourceFork(self):
    """Test the read functionality on a resource fork."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS, data_stream='rsrc', identifier=25,
        location='/a_directory/a_resourcefork', parent=self._raw_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestReadResourceFork(file_object)


if __name__ == '__main__':
  unittest.main()
