#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the operating system file-like object implementation."""

import os
import unittest

from dfvfs.file_io import os_file_io
from dfvfs.path import os_path_spec
from dfvfs.resolver import context


class OSFileTest(unittest.TestCase):
  """The unit test for the operating systesm file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'password.txt')
    self._path_spec1 = os_path_spec.OSPathSpec(location=test_file)

    test_file = os.path.join(u'test_data', u'another_file')
    self._path_spec2 = os_path_spec.OSPathSpec(location=test_file)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = os_file_io.OSFile(self._resolver_context)
    file_object.open(path_spec=self._path_spec1)

    self.assertEquals(file_object.get_size(), 116)
    file_object.close()

    # TODO: add a failing scenario.

  def testSeek(self):
    """Test the seek functionality."""
    file_object = os_file_io.OSFile(self._resolver_context)
    file_object.open(path_spec=self._path_spec2)

    self.assertEquals(file_object.get_size(), 22)

    file_object.seek(10)
    self.assertEquals(file_object.read(5), b'other')
    self.assertEquals(file_object.get_offset(), 15)

    file_object.seek(-10, os.SEEK_END)
    self.assertEquals(file_object.read(5), b'her f')

    file_object.seek(2, os.SEEK_CUR)
    self.assertEquals(file_object.read(2), b'e.')

    # Conforming to the POSIX seek the offset can exceed the file size
    # but reading will result in no data being returned.
    file_object.seek(300, os.SEEK_SET)
    self.assertEquals(file_object.get_offset(), 300)
    self.assertEquals(file_object.read(2), b'')

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
    file_object = os_file_io.OSFile(self._resolver_context)
    file_object.open(path_spec=self._path_spec1)

    read_buffer = file_object.read()

    expected_buffer = (
        b'place,user,password\n'
        b'bank,joesmith,superrich\n'
        b'alarm system,-,1234\n'
        b'treasure chest,-,1111\n'
        b'uber secret laire,admin,admin\n')

    self.assertEquals(read_buffer, expected_buffer)

    file_object.close()

    # TODO: add boundary scenarios.


if __name__ == '__main__':
  unittest.main()
