#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the zip extracted file-like object."""

from __future__ import unicode_literals

import unittest

from dfvfs.file_io import zip_file_io
from dfvfs.path import os_path_spec
from dfvfs.path import zip_path_spec
from dfvfs.resolver import context

from tests.file_io import test_lib


class ZipFileTest(test_lib.SylogTestCase):
  """The unit test for a zip extracted file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(ZipFileTest, self).setUp()
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.zip'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._zip_path_spec = zip_path_spec.ZipPathSpec(
        location='/syslog', parent=path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = zip_file_io.ZipFile(self._resolver_context)
    file_object.open(path_spec=self._zip_path_spec)

    self._TestGetSizeFileObject(file_object)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = zip_file_io.ZipFile(self._resolver_context)
    file_object.open(path_spec=self._zip_path_spec)

    self._TestSeekFileObject(file_object)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = zip_file_io.ZipFile(self._resolver_context)
    file_object.open(path_spec=self._zip_path_spec)

    self._TestReadFileObject(file_object)

    file_object.close()

    # TODO: add tests for read > UNCOMPRESSED_DATA_BUFFER_SIZE


if __name__ == '__main__':
  unittest.main()
