#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the fake file-like object implementation."""

import os
import unittest

from dfvfs.file_io import fake_file_io
from dfvfs.path import fake_path_spec
from dfvfs.resolver import context


class FakeFileTest(unittest.TestCase):
  """The unit test for the operating systesm file-like object."""

  _FILE_DATA1 = (
      b'place,user,password\n'
      b'bank,joesmith,superrich\n'
      b'alarm system,-,1234\n'
      b'treasure chest,-,1111\n'
      b'uber secret laire,admin,admin\n')

  _FILE_DATA2 = (
      b'This is another file.\n')

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = u'/test_data/password.txt'
    self._path_spec1 = fake_path_spec.FakePathSpec(location=test_file)

    test_file = u'/test_data/another_file'
    self._path_spec2 = fake_path_spec.FakePathSpec(location=test_file)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = fake_file_io.FakeFile(
        self._resolver_context, self._FILE_DATA1)
    file_object.open(path_spec=self._path_spec1)

    self.assertEqual(file_object.get_size(), 116)
    file_object.close()

    # TODO: add a failing scenario.

  def testSeek(self):
    """Test the seek functionality."""
    file_object = fake_file_io.FakeFile(
        self._resolver_context, self._FILE_DATA2)
    file_object.open(path_spec=self._path_spec2)

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
    file_object = fake_file_io.FakeFile(
        self._resolver_context, self._FILE_DATA1)
    file_object.open(path_spec=self._path_spec1)

    read_buffer = file_object.read()

    expected_buffer = (
        b'place,user,password\n'
        b'bank,joesmith,superrich\n'
        b'alarm system,-,1234\n'
        b'treasure chest,-,1111\n'
        b'uber secret laire,admin,admin\n')

    self.assertEqual(read_buffer, expected_buffer)

    file_object.close()

    # TODO: add boundary scenarios.


if __name__ == '__main__':
  unittest.main()
