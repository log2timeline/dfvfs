#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the gzip file-like object."""

from __future__ import unicode_literals

import unittest

from dfvfs.file_io import gzip_file_io
from dfvfs.path import gzip_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context

from tests import test_lib as shared_test_lib
from tests.file_io import test_lib


@shared_test_lib.skipUnlessHasTestFile(['syslog.gz'])
class GzipFileTest(test_lib.SylogTestCase):
  """The unit test for a gzip file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.gz'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._gzip_path_spec = gzip_path_spec.GzipPathSpec(parent=path_spec)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = gzip_file_io.GzipFile(self._resolver_context)
    file_object.open(path_spec=self._gzip_path_spec)

    self._TestGetSizeFileObject(file_object)

    self.assertEqual(file_object.modification_times, [0x501416d7])
    self.assertEqual(file_object.operating_systems, [0x03])
    self.assertEqual(file_object.original_filenames, ['syslog.1'])
    self.assertEqual(file_object.comments, [None])

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = gzip_file_io.GzipFile(self._resolver_context)
    file_object.open(path_spec=self._gzip_path_spec)

    self._TestSeekFileObject(file_object)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = gzip_file_io.GzipFile(self._resolver_context)
    file_object.open(path_spec=self._gzip_path_spec)

    self._TestReadFileObject(file_object)

    file_object.close()

  def testReadMultipleMembers(self):
    """Tests reading a file that contains multiple gzip members."""
    test_file = self._GetTestFilePath(['fsevents_000000000000b208'])
    parent_path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = gzip_path_spec.GzipPathSpec(parent=parent_path_spec)
    file_object = gzip_file_io.GzipFile(self._resolver_context)
    file_object.open(path_spec=path_spec)

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

    file_object.close()


if __name__ == '__main__':
  unittest.main()
