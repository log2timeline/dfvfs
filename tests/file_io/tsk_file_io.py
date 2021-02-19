#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using the SleuthKit (TSK)."""

import unittest

from dfvfs.file_io import tsk_file_io
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory

from tests.file_io import test_lib


class TSKFileTestExt2(test_lib.Ext2ImageFileTestCase):
  """Tests the SleuthKit (TSK) file-like object on ext2."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(TSKFileTestExt2, self).setUp()
    test_path = self._GetTestFilePath(['ext2.raw'])
    self._SkipIfPathNotExists(test_path)

    self._os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._os_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._os_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._os_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._os_path_spec)


class TSKFileTestNTFS(test_lib.NTFSImageFileTestCase):
  """Tests the SleuthKit (TSK) file-like object on NTFS."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(TSKFileTestNTFS, self).setUp()
    test_path = self._GetTestFilePath(['ntfs.raw'])
    self._SkipIfPathNotExists(test_path)

    self._os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

  def testOpenCloseMFTEntry(self):
    """Test the open and close functionality using a MFT entry."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._MFT_ENTRY_PASSWORDS_TXT,
        parent=self._os_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context, path_spec)

    self._TestOpenCloseMFTEntry(file_object)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/passwords.txt',
        parent=self._os_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context, path_spec)

    self._TestOpenCloseLocation(file_object)

    # Try open with a path specification that has no parent.
    path_spec.parent = None
    file_object = tsk_file_io.TSKFile(self._resolver_context, path_spec)

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/a_directory/another_file',
        inode=self._MFT_ENTRY_ANOTHER_FILE, parent=self._os_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context, path_spec)

    self._TestSeek(file_object)

  def testRead(self):
    """Test the read functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/passwords.txt',
        inode=self._MFT_ENTRY_PASSWORDS_TXT, parent=self._os_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context, path_spec)

    self._TestRead(file_object)

  def testReadADS(self):
    """Test the read functionality on an alternate data stream (ADS)."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, data_stream='$SDS', location='/$Secure',
        inode=9, parent=self._os_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context, path_spec)

    self._TestReadADS(file_object)


if __name__ == '__main__':
  unittest.main()
