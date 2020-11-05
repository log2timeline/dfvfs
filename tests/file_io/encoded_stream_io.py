#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the encoded stream file-like object."""

from __future__ import unicode_literals

import os
import unittest

from dfvfs.file_io import encoded_stream_io
from dfvfs.file_io import os_file_io
from dfvfs.lib import definitions
from dfvfs.path import encoded_stream_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context

from tests.file_io import test_lib


class Base16EncodedStreamTest(test_lib.SylogTestCase):
  """The unit test for a base16 encoded stream file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.base16'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._encoded_stream_path_spec = (
        encoded_stream_path_spec.EncodedStreamPathSpec(
            encoding_method=definitions.ENCODING_METHOD_BASE16,
            parent=self._os_path_spec))

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    os_file_object = os_file_io.OSFile(self._resolver_context)
    os_file_object.open(path_spec=self._os_path_spec)
    file_object = encoded_stream_io.EncodedStream(
        self._resolver_context,
        encoding_method=definitions.ENCODING_METHOD_BASE16,
        file_object=os_file_object)
    file_object.open()

    self._TestGetSizeFileObject(file_object)

    file_object.close()
    os_file_object.close()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = encoded_stream_io.EncodedStream(self._resolver_context)
    file_object.open(path_spec=self._encoded_stream_path_spec)

    self._TestGetSizeFileObject(file_object)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = encoded_stream_io.EncodedStream(self._resolver_context)
    file_object.open(path_spec=self._encoded_stream_path_spec)

    self._TestSeekFileObject(file_object)

    file_object.close()

    # TODO: Test SEEK_CUR after open.

    # Test SEEK_END after open.
    file_object = encoded_stream_io.EncodedStream(self._resolver_context)
    file_object.open(path_spec=self._encoded_stream_path_spec)

    file_object.seek(-10, os.SEEK_END)
    self.assertEqual(file_object.read(5), b'times')

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = encoded_stream_io.EncodedStream(self._resolver_context)
    file_object.open(path_spec=self._encoded_stream_path_spec)

    self._TestReadFileObject(file_object)

    file_object.close()


class Base32EncodedStreamTest(test_lib.SylogTestCase):
  """The unit test for a base32 encoded stream file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.base32'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._encoded_stream_path_spec = (
        encoded_stream_path_spec.EncodedStreamPathSpec(
            encoding_method=definitions.ENCODING_METHOD_BASE32,
            parent=self._os_path_spec))

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    os_file_object = os_file_io.OSFile(self._resolver_context)
    os_file_object.open(path_spec=self._os_path_spec)
    file_object = encoded_stream_io.EncodedStream(
        self._resolver_context,
        encoding_method=definitions.ENCODING_METHOD_BASE32,
        file_object=os_file_object)
    file_object.open()

    self._TestGetSizeFileObject(file_object)

    file_object.close()
    os_file_object.close()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = encoded_stream_io.EncodedStream(self._resolver_context)
    file_object.open(path_spec=self._encoded_stream_path_spec)

    self._TestGetSizeFileObject(file_object)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = encoded_stream_io.EncodedStream(self._resolver_context)
    file_object.open(path_spec=self._encoded_stream_path_spec)

    self._TestSeekFileObject(file_object)

    file_object.close()

    # TODO: Test SEEK_CUR after open.

    # Test SEEK_END after open.
    file_object = encoded_stream_io.EncodedStream(self._resolver_context)
    file_object.open(path_spec=self._encoded_stream_path_spec)

    file_object.seek(-10, os.SEEK_END)
    self.assertEqual(file_object.read(5), b'times')

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = encoded_stream_io.EncodedStream(self._resolver_context)
    file_object.open(path_spec=self._encoded_stream_path_spec)

    self._TestReadFileObject(file_object)

    file_object.close()


class Base64EncodedStreamTest(test_lib.SylogTestCase):
  """The unit test for a base64 encoded stream file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.base64'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._encoded_stream_path_spec = (
        encoded_stream_path_spec.EncodedStreamPathSpec(
            encoding_method=definitions.ENCODING_METHOD_BASE64,
            parent=self._os_path_spec))

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    os_file_object = os_file_io.OSFile(self._resolver_context)
    os_file_object.open(path_spec=self._os_path_spec)
    file_object = encoded_stream_io.EncodedStream(
        self._resolver_context,
        encoding_method=definitions.ENCODING_METHOD_BASE64,
        file_object=os_file_object)
    file_object.open()

    self._TestGetSizeFileObject(file_object)

    file_object.close()
    os_file_object.close()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = encoded_stream_io.EncodedStream(self._resolver_context)
    file_object.open(path_spec=self._encoded_stream_path_spec)

    self._TestGetSizeFileObject(file_object)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = encoded_stream_io.EncodedStream(self._resolver_context)
    file_object.open(path_spec=self._encoded_stream_path_spec)

    self._TestSeekFileObject(file_object)

    file_object.close()

    # TODO: Test SEEK_CUR after open.

    # Test SEEK_END after open.
    file_object = encoded_stream_io.EncodedStream(self._resolver_context)
    file_object.open(path_spec=self._encoded_stream_path_spec)

    file_object.seek(-10, os.SEEK_END)
    self.assertEqual(file_object.read(5), b'times')

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = encoded_stream_io.EncodedStream(self._resolver_context)
    file_object.open(path_spec=self._encoded_stream_path_spec)

    self._TestReadFileObject(file_object)

    file_object.close()


if __name__ == '__main__':
  unittest.main()
