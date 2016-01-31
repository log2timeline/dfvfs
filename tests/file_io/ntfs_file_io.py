#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pyfsntfs."""

import os
import unittest

from dfvfs.file_io import ntfs_file_io
from dfvfs.lib import errors
from dfvfs.path import ntfs_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.resolver import context
from tests.file_io import test_lib


class NTFSFileTest(test_lib.ImageFileTestCase):
  """The unit test for the NTFS file-like object."""

  _MFT_ENTRY_ANOTHER_FILE = 39
  _MFT_ENTRY_PASSWORDS_TXT = 41

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(NTFSFileTest, self).setUp()
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'vsstest.qcow2')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(
        parent=self._os_path_spec)

  def testOpenCloseMFTEntry(self):
    """Test the open and close functionality using a MFT entry."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=self._MFT_ENTRY_PASSWORDS_TXT,
        parent=self._qcow_path_spec)
    file_object = ntfs_file_io.NTFSFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 116)
    file_object.close()

    # TODO: add a failing scenario.

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=u'\\password.txt', parent=self._qcow_path_spec)
    file_object = ntfs_file_io.NTFSFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 116)
    file_object.close()

    # Try open with a path specification that has no parent.
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=u'/a_directory/another_file',
        mft_attribute=2, mft_entry=self._MFT_ENTRY_ANOTHER_FILE,
        parent=self._qcow_path_spec)
    file_object = ntfs_file_io.NTFSFile(self._resolver_context)

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
    path_spec = ntfs_path_spec.NTFSPathSpec(
        location=u'\\passwords.txt', mft_attribute=2,
        mft_entry=self._MFT_ENTRY_PASSWORDS_TXT, parent=self._qcow_path_spec)
    file_object = ntfs_file_io.NTFSFile(self._resolver_context)

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

  def testReadADS(self):
    """Test the read functionality on an alternate data stream (ADS)."""
    path_spec = ntfs_path_spec.NTFSPathSpec(
        data_stream=u'$SDS', location=u'\\$Secure', mft_attribute=2,
        mft_entry=9, parent=self._qcow_path_spec)
    file_object = ntfs_file_io.NTFSFile(self._resolver_context)

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
