#!/usr/bin/python
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
    test_file2 = self._GetTestFilePath(['fsevents_000000000000b208'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec2 = os_path_spec.OSPathSpec(location=test_file2)
    self._gzip_path_spec = gzip_path_spec.GzipPathSpec(parent=path_spec)
    self._gzip_path_spec2 = gzip_path_spec.GzipPathSpec(parent=path_spec2)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = gzip_file_io.GzipFile(self._resolver_context)
    file_object.open(path_spec=self._gzip_path_spec)

    self._TestGetSizeFileObject(file_object)

    self.assertEqual(file_object.modification_time, 0x501416d7)
    self.assertEqual(file_object.operating_system, 0x03)
    self.assertEqual(file_object.original_filename, 'syslog.1')
    self.assertIsNone(file_object.comment)

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

  def testRead2(self):
    file_object = gzip_file_io.GzipFile(self._resolver_context)
    file_object.open(path_spec=self._gzip_path_spec2)

    content = file_object.read()
    print content

    file_object.close()


if __name__ == '__main__':
  unittest.main()
