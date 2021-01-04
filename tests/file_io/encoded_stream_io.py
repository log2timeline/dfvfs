#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the encoded stream file-like object."""

import os
import unittest

from dfvfs.file_io import encoded_stream_io
from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context

from tests.file_io import test_lib


class Base16EncodedStreamTest(test_lib.SylogTestCase):
  """The unit test for a base16 encoded stream file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['syslog.base16'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._encoded_stream_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ENCODED_STREAM,
        encoding_method=definitions.ENCODING_METHOD_BASE16,
        parent=test_os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    file_object = encoded_stream_io.EncodedStream(
        self._resolver_context, self._encoded_stream_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = encoded_stream_io.EncodedStream(
        self._resolver_context, self._encoded_stream_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    file_object = encoded_stream_io.EncodedStream(
        self._resolver_context, self._encoded_stream_path_spec)
    file_object.Open()

    self._TestSeekFileObject(file_object)

    # TODO: Test SEEK_CUR after open.

    # Test SEEK_END after open.
    file_object = encoded_stream_io.EncodedStream(
        self._resolver_context, self._encoded_stream_path_spec)
    file_object.Open()

    file_object.seek(-10, os.SEEK_END)
    self.assertEqual(file_object.read(5), b'times')

  def testRead(self):
    """Test the read functionality."""
    file_object = encoded_stream_io.EncodedStream(
        self._resolver_context, self._encoded_stream_path_spec)
    file_object.Open()

    self._TestReadFileObject(file_object)


class Base32EncodedStreamTest(test_lib.SylogTestCase):
  """The unit test for a base32 encoded stream file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['syslog.base32'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._encoded_stream_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ENCODED_STREAM,
        encoding_method=definitions.ENCODING_METHOD_BASE32,
        parent=test_os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    file_object = encoded_stream_io.EncodedStream(
        self._resolver_context, self._encoded_stream_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = encoded_stream_io.EncodedStream(
        self._resolver_context, self._encoded_stream_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    file_object = encoded_stream_io.EncodedStream(
        self._resolver_context, self._encoded_stream_path_spec)
    file_object.Open()

    self._TestSeekFileObject(file_object)

    # TODO: Test SEEK_CUR after open.

    # Test SEEK_END after open.
    file_object = encoded_stream_io.EncodedStream(
        self._resolver_context, self._encoded_stream_path_spec)
    file_object.Open()

    file_object.seek(-10, os.SEEK_END)
    self.assertEqual(file_object.read(5), b'times')

  def testRead(self):
    """Test the read functionality."""
    file_object = encoded_stream_io.EncodedStream(
        self._resolver_context, self._encoded_stream_path_spec)
    file_object.Open()

    self._TestReadFileObject(file_object)


class Base64EncodedStreamTest(test_lib.SylogTestCase):
  """The unit test for a base64 encoded stream file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['syslog.base64'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._encoded_stream_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ENCODED_STREAM,
        encoding_method=definitions.ENCODING_METHOD_BASE64,
        parent=test_os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    file_object = encoded_stream_io.EncodedStream(
        self._resolver_context, self._encoded_stream_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = encoded_stream_io.EncodedStream(
        self._resolver_context, self._encoded_stream_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    file_object = encoded_stream_io.EncodedStream(
        self._resolver_context, self._encoded_stream_path_spec)
    file_object.Open()

    self._TestSeekFileObject(file_object)

    # TODO: Test SEEK_CUR after open.

    # Test SEEK_END after open.
    file_object = encoded_stream_io.EncodedStream(
        self._resolver_context, self._encoded_stream_path_spec)
    file_object.Open()

    file_object.seek(-10, os.SEEK_END)
    self.assertEqual(file_object.read(5), b'times')

  def testRead(self):
    """Test the read functionality."""
    file_object = encoded_stream_io.EncodedStream(
        self._resolver_context, self._encoded_stream_path_spec)
    file_object.Open()

    self._TestReadFileObject(file_object)


if __name__ == '__main__':
  unittest.main()
