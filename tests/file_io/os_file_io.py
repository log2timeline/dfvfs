#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the operating system file-like object implementation."""

from __future__ import unicode_literals

import os
import unittest

from dfvfs.file_io import os_file_io
from dfvfs.lib import errors
from dfvfs.path import os_path_spec
from dfvfs.resolver import context

from tests import test_lib as shared_test_lib


# TODO: add tests that mock the device handling behavior.
# TODO: add tests that mock the access denied behavior.

class OSFileTest(shared_test_lib.BaseTestCase):
  """The unit test for the operating system file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['password.txt'])
    self._SkipIfPathNotExists(test_file)

    self._path_spec1 = os_path_spec.OSPathSpec(location=test_file)

    test_file = self._GetTestFilePath(['another_file'])
    self._SkipIfPathNotExists(test_file)

    self._path_spec2 = os_path_spec.OSPathSpec(location=test_file)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = os_file_io.OSFile(self._resolver_context)
    file_object.open(path_spec=self._path_spec1)

    self.assertEqual(file_object.get_size(), 116)
    file_object.close()

    # Try open without a path specification.
    with self.assertRaises(ValueError):
      file_object.open(path_spec=None)

    # Try open with a path specification that has no location.
    test_file = self._GetTestFilePath(['password.txt'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec.location = None

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

    # Try open with a path specification that has a parent.
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec.parent = self._path_spec2

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    file_object = os_file_io.OSFile(self._resolver_context)

    # Try seek without the file object being open.
    with self.assertRaises(IOError):
      file_object.seek(0, os.SEEK_SET)

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
    file_object = os_file_io.OSFile(self._resolver_context)

    # Try read without the file object being open.
    with self.assertRaises(IOError):
      file_object.read()

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

  def testGetOffset(self):
    """Test the get offset functionality."""
    file_object = os_file_io.OSFile(self._resolver_context)

    # Try get_offset without the file object being open.
    with self.assertRaises(IOError):
      file_object.get_offset()

    file_object.open(path_spec=self._path_spec1)

    offset = file_object.get_offset()
    self.assertEqual(offset, 0)

    file_object.close()

  def testGetSize(self):
    """Test the get size functionality."""
    file_object = os_file_io.OSFile(self._resolver_context)

    # Try get_size without the file object being open.
    with self.assertRaises(IOError):
      file_object.get_size()

    file_object.open(path_spec=self._path_spec1)

    size = file_object.get_size()
    self.assertEqual(size, 116)

    file_object.close()


if __name__ == '__main__':
  unittest.main()
