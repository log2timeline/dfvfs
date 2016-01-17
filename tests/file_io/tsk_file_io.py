#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using the SleuthKit (TSK)."""

import os
import unittest

from dfvfs.file_io import tsk_file_io
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import tsk_path_spec
from tests.file_io import test_lib


class TSKFileTest(test_lib.ImageFileTestCase):
  """The unit test for the SleuthKit (TSK) file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(TSKFileTest, self).setUp()
    test_file = os.path.join(u'test_data', u'ímynd.dd')
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

  def testReadADS(self):
    """Test the read functionality on an alternate data stream (ADS)."""
    test_file = os.path.join(u'test_data', u'vsstest.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    path_spec = tsk_path_spec.TSKPathSpec(
        data_stream=u'$SDS', inode=9, location=u'\\$Secure', parent=path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context)

    file_object.open(path_spec=path_spec)

    expected_buffer = (
        b'H\n\x80\xb9\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

    read_buffer = file_object.read(size=16)
    self.assertEqual(read_buffer, expected_buffer)

    file_object.seek(0x00040000, os.SEEK_SET)

    read_buffer = file_object.read(size=16)
    self.assertEqual(read_buffer, expected_buffer)

    file_object.seek(0x000401a0, os.SEEK_SET)

    expected_buffer = (
        b'\xc3\xb4\xb1\x34\x03\x01\x00\x00\xa0\x01\x00\x00\x00\x00\x00\x00')

    read_buffer = file_object.read(size=16)
    self.assertEqual(read_buffer, expected_buffer)


if __name__ == '__main__':
  unittest.main()
