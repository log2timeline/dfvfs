#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the zip extracted file-like object."""

import unittest

from dfvfs.file_io import zip_file_io
from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context

from tests.file_io import test_lib


class ZipFileTest(test_lib.SylogTestCase):
  """Tests a zip extracted file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(ZipFileTest, self).setUp()
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['syslog.zip'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._zip_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ZIP, location='/syslog',
        parent=test_os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = zip_file_io.ZipFile(
        self._resolver_context, self._zip_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    file_object = zip_file_io.ZipFile(
        self._resolver_context, self._zip_path_spec)
    file_object.Open()

    self._TestSeekFileObject(file_object)

  def testRead(self):
    """Test the read functionality."""
    file_object = zip_file_io.ZipFile(
        self._resolver_context, self._zip_path_spec)
    file_object.Open()

    self._TestReadFileObject(file_object)

    # TODO: add tests for read > UNCOMPRESSED_DATA_BUFFER_SIZE


if __name__ == '__main__':
  unittest.main()
