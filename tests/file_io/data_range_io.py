#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the data range file-like object."""

from __future__ import unicode_literals

import unittest

from dfvfs.file_io import data_range_io
from dfvfs.file_io import os_file_io
from dfvfs.path import data_range_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context

from tests.file_io import test_lib


class DataRangeTest(test_lib.SylogTestCase):
  """The unit test for the data range file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._data_range_path_spec = data_range_path_spec.DataRangePathSpec(
        range_offset=167, range_size=1080, parent=self._os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    os_file_object = os_file_io.OSFile(self._resolver_context)
    os_file_object.open(path_spec=self._os_path_spec)
    file_object = data_range_io.DataRange(
        self._resolver_context, file_object=os_file_object)
    file_object.open()

    self._TestGetSizeFileObject(file_object)

    file_object.close()
    os_file_object.close()

  def testSetRange(self):
    """Test the set data range functionality."""
    os_file_object = os_file_io.OSFile(self._resolver_context)
    os_file_object.open(path_spec=self._os_path_spec)
    file_object = data_range_io.DataRange(
        self._resolver_context, file_object=os_file_object)
    file_object.SetRange(167, 1080)
    file_object.open()

    self.assertEqual(file_object.get_size(), 1080)

    file_object.close()
    os_file_object.close()

    # TODO: add some edge case testing here.

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = data_range_io.DataRange(self._resolver_context)
    file_object.open(path_spec=self._data_range_path_spec)

    self.assertEqual(file_object.get_size(), 1080)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = data_range_io.DataRange(self._resolver_context)
    file_object.open(path_spec=self._data_range_path_spec)

    self._TestSeekFileObject(file_object, base_offset=0)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = data_range_io.DataRange(self._resolver_context)
    file_object.open(path_spec=self._data_range_path_spec)

    self._TestReadFileObject(file_object, base_offset=0)

    file_object.close()


if __name__ == '__main__':
  unittest.main()
