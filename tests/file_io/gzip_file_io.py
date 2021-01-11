#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the gzip file-like object."""

import unittest

from dfvfs.file_io import gzip_file_io
from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context

from tests.file_io import test_lib


class GzipFileTest(test_lib.SylogTestCase):
  """Tests a gzip file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['syslog.gz'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._gzip_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GZIP, parent=test_os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = gzip_file_io.GzipFile(
        self._resolver_context, self._gzip_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

    self.assertEqual(file_object.modification_times, [0x501416d7])
    self.assertEqual(file_object.operating_systems, [0x03])
    self.assertEqual(file_object.original_filenames, ['syslog.1'])
    self.assertEqual(file_object.comments, [None])

  def testSeek(self):
    """Test the seek functionality."""
    file_object = gzip_file_io.GzipFile(
        self._resolver_context, self._gzip_path_spec)
    file_object.Open()

    self._TestSeekFileObject(file_object)

  def testRead(self):
    """Test the read functionality."""
    file_object = gzip_file_io.GzipFile(
        self._resolver_context, self._gzip_path_spec)
    file_object.Open()

    self._TestReadFileObject(file_object)

  def testReadCorrupt(self):
    """Tests reading a file that is corrupt."""
    # The corrupt gzip has no member footer.
    test_path = self._GetTestFilePath(['corrupt1.gz'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_gzip_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GZIP, parent=test_os_path_spec)

    file_object = gzip_file_io.GzipFile(
        self._resolver_context, test_gzip_path_spec)
    file_object.Open()

    self.assertEqual(file_object.uncompressed_data_size, 2994187)

  def testReadMultipleMembers(self):
    """Tests reading a file that contains multiple gzip members."""
    test_path = self._GetTestFilePath(['fsevents_000000000000b208'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_gzip_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GZIP, parent=test_os_path_spec)

    file_object = gzip_file_io.GzipFile(
        self._resolver_context, test_gzip_path_spec)
    file_object.Open()

    self.assertEqual(file_object.uncompressed_data_size, 506631)
    self.assertEqual(file_object.modification_times, [0, 0])
    self.assertEqual(file_object.operating_systems, [3, 3])
    self.assertEqual(file_object.original_filenames, [None, None])
    self.assertEqual(file_object.comments, [None, None])

    file_start = file_object.read(4)
    self.assertEqual(file_start, b'1SLD')

    # Read the end of the second member
    file_object.seek(506631 - 4)
    file_end = file_object.read(4)
    self.assertEqual(file_end, b'\x02\x00\x80\x00')

    # Seek backwards, and read across a member boundary.
    file_object.seek(28530)
    self.assertEqual(file_object.read(6), b'OS\x00P\x07\x00')

    # Read with a size greater than the file size.
    file_object.seek(0)
    data = file_object.read(size=506631 + 4)
    self.assertEqual(len(data), 506631)
    self.assertEqual(data[-4:], b'\x02\x00\x80\x00')


if __name__ == '__main__':
  unittest.main()
