#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The PyVFS Project Authors.
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
"""Tests for the file-like object implementation using the SleuthKit (TSK)."""

import os
import pytsk3
import unittest

from pyvfs.io import tsk_file
from pyvfs.path import tsk_path_spec


class TSKFileTest(unittest.TestCase):
  """The unit test for the SleuthKit (TSK) file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = os.path.join('test_data', 'image.dd')
    # Need to keep the pytsk3.Img_Info around due to issue
    # with reference counting.
    self._tsk_image = pytsk3.Img_Info(test_file)
    self._tsk_file_system = pytsk3.FS_Info(self._tsk_image, offset=0)

  def testOpenCloseInode(self):
    """Test the open and close functionality."""
    path_spec = tsk_path_spec.TSKPathSpec(inode=15)
    file_object = tsk_file.TSKFile(self._tsk_file_system)

    file_object.open(path_spec)
    self.assertEquals(file_object.get_size(), 116)
    file_object.close()

    # TODO: add a failing scenario.

  def testOpenCloseLocation(self):
    """Test the open and close functionality."""
    path_spec = tsk_path_spec.TSKPathSpec(location='/passwords.txt')
    file_object = tsk_file.TSKFile(self._tsk_file_system)

    file_object.open(path_spec)
    self.assertEquals(file_object.get_size(), 116)
    file_object.close()

    # TODO: add a failing scenario.

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=16, location='/a_directory/another_file')
    file_object = tsk_file.TSKFile(self._tsk_file_system)

    file_object.open(path_spec)
    self.assertEquals(file_object.get_size(), 22)

    file_object.seek(10)
    self.assertEquals(file_object.read(5), 'other')
    self.assertEquals(file_object.get_offset(), 15)

    file_object.seek(-10, os.SEEK_END)
    self.assertEquals(file_object.read(5), 'her f')

    file_object.seek(2, os.SEEK_CUR)
    self.assertEquals(file_object.read(2), 'e.')

    # Conforming to the POSIX seek the offset can exceed the file size
    # but reading will result in no data being returned.
    file_object.seek(300, os.SEEK_SET)
    self.assertEquals(file_object.get_offset(), 300)
    self.assertEquals(file_object.read(2), '')

    with self.assertRaises(IOError):
      file_object.seek(-10, os.SEEK_SET)

    # On error the offset should not change.
    self.assertEquals(file_object.get_offset(), 300)

    with self.assertRaises(IOError):
      file_object.seek(10, 5)

    # On error the offset should not change.
    self.assertEquals(file_object.get_offset(), 300)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    path_spec = tsk_path_spec.TSKPathSpec(inode=15, location='/passwords.txt')
    file_object = tsk_file.TSKFile(self._tsk_file_system)

    file_object.open(path_spec)
    read_buffer = file_object.read()

    expected_buffer = (
        'place,user,password\n'
        'bank,joesmith,superrich\n'
        'alarm system,-,1234\n'
        'treasure chest,-,1111\n'
        'uber secret laire,admin,admin\n')

    self.assertEquals(read_buffer, expected_buffer)

    file_object.close()

    # TODO: add boundary scenarios.


if __name__ == '__main__':
  unittest.main()
