#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The dfVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for the file-like object implementation using VSS."""

import os
import unittest

from dfvfs.lib import errors
from dfvfs.file_io import vshadow_file_io
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import vshadow_path_spec


class VShadowFileTest(unittest.TestCase):
  """The unit test for the Volume Shadow Snapshots (VSS) file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = os.path.join('test_data', 'vsstest.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QcowPathSpec(parent=path_spec)

  def testOpenClose(self):
    """Test the open and close functionality."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._qcow_path_spec)
    file_object = vshadow_file_io.VShadowFile()

    file_object.open(path_spec)
    self.assertEquals(file_object.get_size(), 0x40000000)
    file_object.close()

    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=13, parent=self._qcow_path_spec)
    file_object = vshadow_file_io.VShadowFile()

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/vss1', parent=self._qcow_path_spec)
    file_object = vshadow_file_io.VShadowFile()

    file_object.open(path_spec)
    self.assertEquals(file_object.get_size(), 0x40000000)
    file_object.close()

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/vss0', parent=self._qcow_path_spec)
    file_object = vshadow_file_io.VShadowFile()

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/vss13', parent=self._qcow_path_spec)
    file_object = vshadow_file_io.VShadowFile()

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._qcow_path_spec)
    file_object = vshadow_file_io.VShadowFile()

    file_object.open(path_spec)
    self.assertEquals(file_object.get_size(), 0x40000000)

    file_object.seek(0x1e0)
    self.assertEquals(file_object.get_offset(), 0x1e0)
    self.assertEquals(file_object.read(16), 'rl+Alt+Del to re')
    self.assertEquals(file_object.get_offset(), 0x1f0)

    file_object.seek(-40, os.SEEK_END)
    self.assertEquals(file_object.get_offset(), 0x3fffffd8)
    self.assertEquals(file_object.read(8), 'Press Ct')
    self.assertEquals(file_object.get_offset(), 0x3fffffe0)

    file_object.seek(3, os.SEEK_CUR)
    self.assertEquals(file_object.get_offset(), 0x3fffffe3)
    self.assertEquals(file_object.read(7), 'Alt+Del')
    self.assertEquals(file_object.get_offset(), 0x3fffffea)

    # Conforming to the POSIX seek the offset can exceed the file size
    # but reading will result in no data being returned.
    expected_offset = 0x40000000 + 100
    file_object.seek(expected_offset, os.SEEK_SET)
    self.assertEquals(file_object.get_offset(), expected_offset)
    self.assertEquals(file_object.read(20), '')

    with self.assertRaises(IOError):
      file_object.seek(-10, os.SEEK_SET)

    # On error the offset should not change.
    self.assertEquals(file_object.get_offset(), expected_offset)

    with self.assertRaises(IOError):
      file_object.seek(10, 5)

    # On error the offset should not change.
    self.assertEquals(file_object.get_offset(), expected_offset)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._qcow_path_spec)
    file_object = vshadow_file_io.VShadowFile()

    file_object.open(path_spec)
    self.assertEquals(file_object.get_size(), 0x40000000)

    file_object.seek(0x18e)

    expected_data = 'A disk read error occurred\x00\r\nBOOTMGR is missing'
    self.assertEquals(file_object.read(47), expected_data)

    file_object.close()


if __name__ == '__main__':
  unittest.main()
