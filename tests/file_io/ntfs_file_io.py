#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pyfsntfs."""

import unittest

from dfvfs.file_io import ntfs_file_io
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory

from tests.file_io import test_lib


class NTFSFileTest(test_lib.NTFSImageFileTestCase):
  """Tests the NTFS file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(NTFSFileTest, self).setUp()
    test_path = self._GetTestFilePath(['ntfs.raw'])
    self._SkipIfPathNotExists(test_path)

    self._os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

  def testOpenCloseMFTEntry(self):
    """Test the open and close functionality using a MFT entry."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, mft_attribute=1,
        mft_entry=self._MFT_ENTRY_PASSWORDS_TXT, parent=self._os_path_spec)
    file_object = ntfs_file_io.NTFSFile(self._resolver_context, path_spec)

    self._TestOpenCloseMFTEntry(file_object)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\passwords.txt',
        parent=self._os_path_spec)
    file_object = ntfs_file_io.NTFSFile(self._resolver_context, path_spec)

    self._TestOpenCloseLocation(file_object)

    # Try open with a path specification that has no parent.
    path_spec.parent = None
    file_object = ntfs_file_io.NTFSFile(self._resolver_context, path_spec)

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\a_directory\\another_file',
        mft_attribute=2, mft_entry=self._MFT_ENTRY_ANOTHER_FILE,
        parent=self._os_path_spec)
    file_object = ntfs_file_io.NTFSFile(self._resolver_context, path_spec)

    self._TestSeek(file_object)

  def testRead(self):
    """Test the read functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\passwords.txt',
        mft_attribute=2, mft_entry=self._MFT_ENTRY_PASSWORDS_TXT,
        parent=self._os_path_spec)
    file_object = ntfs_file_io.NTFSFile(self._resolver_context, path_spec)

    self._TestRead(file_object)

  def testReadADS(self):
    """Test the read functionality on an alternate data stream (ADS)."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, data_stream='$SDS',
        location='\\$Secure', mft_attribute=2, mft_entry=9,
        parent=self._os_path_spec)
    file_object = ntfs_file_io.NTFSFile(self._resolver_context, path_spec)

    self._TestReadADS(file_object)


if __name__ == '__main__':
  unittest.main()
