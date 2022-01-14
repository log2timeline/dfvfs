#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pyphdi."""

import unittest

from dfvfs.file_io import hfs_file_io
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory

from tests.file_io import test_lib


class PHDIFileTest(test_lib.HFSImageFileTestCase):
  """Tests the PHDI image file-like object."""

  _IDENTIFIER_ANOTHER_FILE = 27
  _IDENTIFIER_PASSWORDS_TXT = 26

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(PHDIFileTest, self).setUp()
    test_path = self._GetTestFilePath(['hfsplus.hdd', 'DiskDescriptor.xml'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._phdi_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_PHDI, parent=test_os_path_spec)
    self._gpt_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GPT, location='/p1',
        parent=self._phdi_path_spec)

  def testOpenCloseIdentifier(self):
    """Test the open and close functionality using an identifier."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS,
        identifier=self._IDENTIFIER_PASSWORDS_TXT, parent=self._gpt_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestOpenCloseIdentifier(file_object)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS,
        identifier=self._IDENTIFIER_PASSWORDS_TXT, location='/passwords.txt',
        parent=self._gpt_path_spec)
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
        definitions.TYPE_INDICATOR_HFS,
        identifier=self._IDENTIFIER_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._gpt_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestSeek(file_object)

  def testRead(self):
    """Test the read functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS,
        identifier=self._IDENTIFIER_PASSWORDS_TXT, location='/passwords.txt',
        parent=self._gpt_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestRead(file_object)


if __name__ == '__main__':
  unittest.main()
