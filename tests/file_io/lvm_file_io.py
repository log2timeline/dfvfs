#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pyvslvm."""

import os
import unittest

from dfvfs.lib import errors
from dfvfs.file_io import lvm_file_io
from dfvfs.path import lvm_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.resolver import context

from tests.file_io import test_lib


class LVMFileTest(unittest.TestCase):
  """The unit test for the Logical Volume Manager (LVM) file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'lvmtest.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)

  def testOpenClose(self):
    """Test the open and close functionality."""
    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._qcow_path_spec, volume_index=1)
    file_object = lvm_file_io.LVMFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 4194304)
    file_object.close()

    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._qcow_path_spec, volume_index=13)
    file_object = lvm_file_io.LVMFile(self._resolver_context)

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

    path_spec = lvm_path_spec.LVMPathSpec(
        location=u'/lvm1', parent=self._qcow_path_spec)
    file_object = lvm_file_io.LVMFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 8388608)
    file_object.close()

    path_spec = lvm_path_spec.LVMPathSpec(
        location=u'/lvm0', parent=self._qcow_path_spec)
    file_object = lvm_file_io.LVMFile(self._resolver_context)

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

    path_spec = lvm_path_spec.LVMPathSpec(
        location=u'/lvm13', parent=self._qcow_path_spec)
    file_object = lvm_file_io.LVMFile(self._resolver_context)

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._qcow_path_spec, volume_index=0)
    file_object = lvm_file_io.LVMFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 8388608)

    file_object.seek(0x488)
    self.assertEqual(file_object.get_offset(), 0x488)
    self.assertEqual(file_object.read(16), b'/home/username/s')
    self.assertEqual(file_object.get_offset(), 0x498)

    file_object.seek(-1047544, os.SEEK_END)
    self.assertEqual(file_object.get_offset(), 0x00700408)
    self.assertEqual(file_object.read(8), b'er,passw')
    self.assertEqual(file_object.get_offset(), 0x00700410)

    file_object.seek(3, os.SEEK_CUR)
    self.assertEqual(file_object.get_offset(), 0x00700413)
    self.assertEqual(file_object.read(7), b'\nbank,j')
    self.assertEqual(file_object.get_offset(), 0x0070041a)

    # Conforming to the POSIX seek the offset can exceed the file size
    # but reading will result in no data being returned.
    expected_offset = 8388608 + 100
    file_object.seek(expected_offset, os.SEEK_SET)
    self.assertEqual(file_object.get_offset(), expected_offset)
    self.assertEqual(file_object.read(20), b'')

    with self.assertRaises(IOError):
      file_object.seek(-10, os.SEEK_SET)

    # On error the offset should not change.
    self.assertEqual(file_object.get_offset(), expected_offset)

    with self.assertRaises(IOError):
      file_object.seek(10, 5)

    # On error the offset should not change.
    self.assertEqual(file_object.get_offset(), expected_offset)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._qcow_path_spec, volume_index=0)
    file_object = lvm_file_io.LVMFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 8388608)

    file_object.seek(0x80400)

    expected_data = (
        b'This is a text file.\n\nWe should be able to parse it.\n')
    self.assertEqual(file_object.read(53), expected_data)

    file_object.close()


class LVMImageFileTest(test_lib.ImageFileTestCase):
  """The unit test for the Logical Volume Manager (LVM) file-like object."""

  _INODE_ANOTHER_FILE = 14
  _INODE_PASSWORDS_TXT = 15

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(LVMImageFileTest, self).setUp()
    test_file = os.path.join(u'test_data', u'lvmtest.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    self._lvm_path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._qcow_path_spec, volume_index=0)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._lvm_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._lvm_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._lvm_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._lvm_path_spec)


if __name__ == '__main__':
  unittest.main()
