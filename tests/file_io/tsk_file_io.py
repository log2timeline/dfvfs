#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using the SleuthKit (TSK)."""

from __future__ import unicode_literals

import unittest

from dfvfs.file_io import tsk_file_io
from dfvfs.path import os_path_spec
from dfvfs.path import tsk_path_spec

from tests.file_io import test_lib


class TSKFileTestExt2(test_lib.Ext2ImageFileTestCase):
  """Tests the SleuthKit (TSK) file-like object on ext2."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(TSKFileTestExt2, self).setUp()
    test_file = self._GetTestFilePath(['ext2.raw'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)

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
    test_file = self._GetTestFilePath(['ntfs.raw'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)

  def testOpenCloseMFTEntry(self):
    """Test the open and close functionality using a MFT entry."""
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=self._MFT_ENTRY_PASSWORDS_TXT, parent=self._os_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context)

    self._TestOpenCloseMFTEntry(path_spec, file_object)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    path_spec = tsk_path_spec.TSKPathSpec(
        location='/passwords.txt', parent=self._os_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context)

    self._TestOpenCloseLocation(path_spec, file_object)

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = tsk_path_spec.TSKPathSpec(
        location='/a_directory/another_file',
        inode=self._MFT_ENTRY_ANOTHER_FILE, parent=self._os_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context)

    self._TestSeek(path_spec, file_object)

  def testRead(self):
    """Test the read functionality."""
    path_spec = tsk_path_spec.TSKPathSpec(
        location='/passwords.txt', inode=self._MFT_ENTRY_PASSWORDS_TXT,
        parent=self._os_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context)

    self._TestRead(path_spec, file_object)

  def testReadADS(self):
    """Test the read functionality on an alternate data stream (ADS)."""
    path_spec = tsk_path_spec.TSKPathSpec(
        data_stream='$SDS', location='/$Secure', inode=9,
        parent=self._os_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context)

    self._TestReadADS(path_spec, file_object)


if __name__ == '__main__':
  unittest.main()
