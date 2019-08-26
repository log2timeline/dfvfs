#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pyfsntfs."""

from __future__ import unicode_literals

import unittest

from dfvfs.file_io import ntfs_file_io
from dfvfs.path import ntfs_path_spec
from dfvfs.path import os_path_spec

from tests.file_io import test_lib


class NTFSFileTest(test_lib.NTFSImageFileTestCase):
  """Tests the NTFS file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(NTFSFileTest, self).setUp()
    test_file = self._GetTestFilePath(['ntfs.raw'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)

  def testOpenCloseMFTEntry(self):
    """Test the open and close functionality using a MFT entry."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=self._MFT_ENTRY_PASSWORDS_TXT,
        parent=self._os_path_spec)
    file_object = ntfs_file_io.NTFSFile(self._resolver_context)

    self._TestOpenCloseMFTEntry(path_spec, file_object)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\passwords.txt', parent=self._os_path_spec)
    file_object = ntfs_file_io.NTFSFile(self._resolver_context)

    self._TestOpenCloseLocation(path_spec, file_object)

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\a_directory\\another_file',
        mft_attribute=2, mft_entry=self._MFT_ENTRY_ANOTHER_FILE,
        parent=self._os_path_spec)
    file_object = ntfs_file_io.NTFSFile(self._resolver_context)

    self._TestSeek(path_spec, file_object)

  def testRead(self):
    """Test the read functionality."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\passwords.txt', mft_attribute=2,
        mft_entry=self._MFT_ENTRY_PASSWORDS_TXT, parent=self._os_path_spec)
    file_object = ntfs_file_io.NTFSFile(self._resolver_context)

    self._TestRead(path_spec, file_object)

  def testReadADS(self):
    """Test the read functionality on an alternate data stream (ADS)."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        data_stream='$SDS', location='\\$Secure', mft_attribute=2,
        mft_entry=9, parent=self._os_path_spec)
    file_object = ntfs_file_io.NTFSFile(self._resolver_context)

    self._TestReadADS(path_spec, file_object)


if __name__ == '__main__':
  unittest.main()
