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
"""Tests for the file-like object implementation using the operating system."""

import os
import unittest

from pyvfs.file_io import os_file_io
from pyvfs.path import os_path_spec


class OSFileTest(unittest.TestCase):
  """The unit test for the operating systesm file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = os.path.join('test_data', 'password.txt')
    self._path_spec1 = os_path_spec.OSPathSpec(location=test_file)

    test_file = os.path.join('test_data', 'another_file')
    self._path_spec2 = os_path_spec.OSPathSpec(location=test_file)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = os_file_io.OSFile()
    file_object.open(self._path_spec1)

    self.assertEquals(file_object.get_size(), 116)
    file_object.close()

    # TODO: add a failing scenario.

  def testSeek(self):
    """Test the seek functionality."""
    file_object = os_file_io.OSFile()
    file_object.open(self._path_spec2)

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
    file_object = os_file_io.OSFile()
    file_object.open(self._path_spec1)

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
