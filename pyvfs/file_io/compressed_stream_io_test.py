#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The PyVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for the compressed stream file-like object."""

import os
import unittest

from pyvfs.file_io import compressed_stream_io
from pyvfs.file_io import os_file_io
from pyvfs.file_io import test_lib
from pyvfs.lib import definitions
from pyvfs.path import compressed_stream_path_spec
from pyvfs.path import os_path_spec


class Bzip2CompressedStreamTest(test_lib.SylogTestCase):
  """The unit test for a bzip2 compressed stream file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = os.path.join('test_data', 'syslog.bz2')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._compressed_stream_path_spec = (
        compressed_stream_path_spec.CompressedStreamPathSpec(
            compression_method=definitions.COMPRESSION_METHOD_BZIP2,
            parent=self._os_path_spec))

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    os_file_object = os_file_io.OSFile()
    os_file_object.open(self._os_path_spec)
    file_object = compressed_stream_io.CompressedStream(
        definitions.COMPRESSION_METHOD_BZIP2, file_object=os_file_object)
    file_object.open()

    self._testGetSizeFileObject(file_object)

    file_object.close()
    os_file_object.close()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = compressed_stream_io.CompressedStream()
    file_object.open(self._compressed_stream_path_spec)

    self._testGetSizeFileObject(file_object)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = compressed_stream_io.CompressedStream()
    file_object.open(self._compressed_stream_path_spec)

    self._testSeekFileObject(file_object)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = compressed_stream_io.CompressedStream()
    file_object.open(self._compressed_stream_path_spec)

    self._testReadFileObject(file_object)

    file_object.close()


class ZlibCompressedStreamTest(test_lib.SylogTestCase):
  """The unit test for a zlib compressed stream file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = os.path.join('test_data', 'syslog.zlib')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._compressed_stream_path_spec = (
        compressed_stream_path_spec.CompressedStreamPathSpec(
            compression_method=definitions.COMPRESSION_METHOD_ZLIB,
            parent=self._os_path_spec))

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    os_file_object = os_file_io.OSFile()
    os_file_object.open(self._os_path_spec)
    file_object = compressed_stream_io.CompressedStream(
        definitions.COMPRESSION_METHOD_ZLIB, file_object=os_file_object)
    file_object.open()

    self._testGetSizeFileObject(file_object)

    file_object.close()
    os_file_object.close()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = compressed_stream_io.CompressedStream()
    file_object.open(self._compressed_stream_path_spec)

    self._testGetSizeFileObject(file_object)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = compressed_stream_io.CompressedStream()
    file_object.open(self._compressed_stream_path_spec)

    self._testSeekFileObject(file_object)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = compressed_stream_io.CompressedStream()
    file_object.open(self._compressed_stream_path_spec)

    self._testReadFileObject(file_object)

    file_object.close()


if __name__ == '__main__':
  unittest.main()
