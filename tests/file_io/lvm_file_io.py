#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pyvslvm."""

from __future__ import unicode_literals

import os
import unittest

from dfvfs.lib import errors
from dfvfs.file_io import lvm_file_io
from dfvfs.path import lvm_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import raw_path_spec
from dfvfs.resolver import context

from tests import test_lib as shared_test_lib
from tests.file_io import test_lib


class LVMFileTest(shared_test_lib.BaseTestCase):
  """The unit test for the Logical Volume Manager (LVM) file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['lvm.raw'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._raw_path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenClose(self):
    """Test the open and close functionality."""
    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._raw_path_spec, volume_index=0)
    file_object = lvm_file_io.LVMFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 4194304)
    file_object.close()

    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._raw_path_spec, volume_index=9)
    file_object = lvm_file_io.LVMFile(self._resolver_context)

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/lvm1', parent=self._raw_path_spec)
    file_object = lvm_file_io.LVMFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 4194304)
    file_object.close()

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/lvm0', parent=self._raw_path_spec)
    file_object = lvm_file_io.LVMFile(self._resolver_context)

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/lvm9', parent=self._raw_path_spec)
    file_object = lvm_file_io.LVMFile(self._resolver_context)

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._raw_path_spec, volume_index=0)
    file_object = lvm_file_io.LVMFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 4194304)

    file_object.seek(0x488)
    self.assertEqual(file_object.get_offset(), 0x00000488)
    self.assertEqual(file_object.read(11), b'/mnt/dfvfs\x00')
    self.assertEqual(file_object.get_offset(), 0x00000493)

    file_object.seek(-1047544, os.SEEK_END)
    self.assertEqual(file_object.get_offset(), 0x00300408)
    self.assertEqual(file_object.read(8), b'er,passw')
    self.assertEqual(file_object.get_offset(), 0x00300410)

    file_object.seek(3, os.SEEK_CUR)
    self.assertEqual(file_object.get_offset(), 0x00300413)
    self.assertEqual(file_object.read(7), b'\nbank,j')
    self.assertEqual(file_object.get_offset(), 0x0030041a)

    # Conforming to the POSIX seek the offset can exceed the file size
    # but reading will result in no data being returned.
    expected_offset = 4194304 + 100
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
        parent=self._raw_path_spec, volume_index=0)
    file_object = lvm_file_io.LVMFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 4194304)

    file_object.seek(0x80400)

    expected_data = (
        b'This is a text file.\n\nWe should be able to parse it.\n')
    self.assertEqual(file_object.read(53), expected_data)

    file_object.close()


class LVMImageFileTest(test_lib.Ext2ImageFileTestCase):
  """Tests the Logical Volume Manager (LVM) file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(LVMImageFileTest, self).setUp()
    test_file = self._GetTestFilePath(['lvm.raw'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._raw_path_spec = raw_path_spec.RawPathSpec(parent=path_spec)
    self._lvm_path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._raw_path_spec, volume_index=0)

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
