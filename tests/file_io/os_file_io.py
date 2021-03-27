#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the operating system file-like object implementation."""

import os
import unittest

from dfvfs.file_io import os_file_io
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context

from tests import test_lib as shared_test_lib


# TODO: add tests that mock the device handling behavior.
# TODO: add tests that mock the access denied behavior.

class OSFileTest(shared_test_lib.BaseTestCase):
  """The unit test for the operating system file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['password.txt'])
    self._SkipIfPathNotExists(test_path)

    self._path_spec1 = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    test_path = self._GetTestFilePath(['another_file'])
    self._SkipIfPathNotExists(test_path)

    self._path_spec2 = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = os_file_io.OSFile(self._resolver_context, self._path_spec1)
    file_object.Open()

    self.assertEqual(file_object.get_size(), 116)

    # Try open without a path specification.
    with self.assertRaises(ValueError):
      file_object = os_file_io.OSFile(self._resolver_context, None)
      file_object.Open()

    # Try open with a path specification that has no location.
    test_path = self._GetTestFilePath(['password.txt'])
    self._SkipIfPathNotExists(test_path)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    path_spec.location = None

    with self.assertRaises(errors.PathSpecError):
      file_object = os_file_io.OSFile(self._resolver_context, path_spec)
      file_object.Open()

    # Try open with a path specification that has a parent.
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    path_spec.parent = self._path_spec2

    with self.assertRaises(errors.PathSpecError):
      file_object = os_file_io.OSFile(self._resolver_context, path_spec)
      file_object.Open()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = os_file_io.OSFile(self._resolver_context, self._path_spec2)

    # Try seek without the file object being open.
    with self.assertRaises(IOError):
      file_object.seek(0, os.SEEK_SET)

    file_object.Open()

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

  def testRead(self):
    """Test the read functionality."""
    file_object = os_file_io.OSFile(self._resolver_context, self._path_spec1)

    # Try read without the file object being open.
    with self.assertRaises(IOError):
      file_object.read()

    file_object.Open()

    read_buffer = file_object.read()

    expected_buffer = (
        b'place,user,password\n'
        b'bank,joesmith,superrich\n'
        b'alarm system,-,1234\n'
        b'treasure chest,-,1111\n'
        b'uber secret laire,admin,admin\n')

    self.assertEqual(read_buffer, expected_buffer)

    # TODO: add boundary scenarios.

  def testGetOffset(self):
    """Test the get offset functionality."""
    file_object = os_file_io.OSFile(self._resolver_context, self._path_spec1)

    # Try get_offset without the file object being open.
    with self.assertRaises(IOError):
      file_object.get_offset()

    file_object.Open()

    offset = file_object.get_offset()
    self.assertEqual(offset, 0)

  def testGetSize(self):
    """Test the get size functionality."""
    file_object = os_file_io.OSFile(self._resolver_context, self._path_spec1)

    # Try get_size without the file object being open.
    with self.assertRaises(IOError):
      file_object.get_size()

    file_object.Open()

    size = file_object.get_size()
    self.assertEqual(size, 116)


if __name__ == '__main__':
  unittest.main()
