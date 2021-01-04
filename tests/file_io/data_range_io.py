#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the data range file-like object."""

import unittest

from dfvfs.file_io import data_range_io
from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context

from tests.file_io import test_lib


class DataRangeTest(test_lib.SylogTestCase):
  """Tests for the data range file-like object."""

  # pylint: disable=protected-access

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['syslog'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._data_range_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_DATA_RANGE, parent=test_os_path_spec,
        range_offset=167, range_size=1080)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    file_object = data_range_io.DataRange(
        self._resolver_context, self._data_range_path_spec)
    file_object.Open()

    self.assertEqual(file_object.get_size(), 1080)

  def testSetRange(self):
    """Test the _SetRange function."""
    file_object = data_range_io.DataRange(
        self._resolver_context, self._data_range_path_spec)

    self.assertEqual(file_object._range_offset, -1)
    self.assertEqual(file_object._range_size, -1)

    file_object._SetRange(167, 1080)

    self.assertEqual(file_object._range_offset, 167)
    self.assertEqual(file_object._range_size, 1080)

    with self.assertRaises(ValueError):
      file_object._SetRange(-1, 1080)

    with self.assertRaises(ValueError):
      file_object._SetRange(167, -1)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = data_range_io.DataRange(
        self._resolver_context, self._data_range_path_spec)
    file_object.Open()

    self.assertEqual(file_object.get_size(), 1080)

  def testSeek(self):
    """Test the seek functionality."""
    file_object = data_range_io.DataRange(
        self._resolver_context, self._data_range_path_spec)
    file_object.Open()

    self._TestSeekFileObject(file_object, base_offset=0)

  def testRead(self):
    """Test the read functionality."""
    file_object = data_range_io.DataRange(
        self._resolver_context, self._data_range_path_spec)
    file_object.Open()

    self._TestReadFileObject(file_object, base_offset=0)


if __name__ == '__main__':
  unittest.main()
