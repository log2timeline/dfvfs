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

from pyvfs.io import compressed_stream
from pyvfs.io import os_file
from pyvfs.lib import definitions
from pyvfs.path import compressed_stream_path_spec
from pyvfs.path import os_path_spec


class CompressedStreamTest(unittest.TestCase):
  """The unit test for the compressed stream file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    location = os.path.join('test_data', 'syslog.bz2')
    self._os_path_spec = os_path_spec.OSPathSpec(location=location)
    self._compressed_stream_path_spec = (
        compressed_stream_path_spec.CompressedStreamPathSpec(
            definitions.COMPRESSION_METHOD_BZIP2, parent=self._os_path_spec))

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    os_file_object = os_file.OSFile()
    os_file_object.open(self._os_path_spec)
    file_object = compressed_stream.CompressedStream(
        definitions.COMPRESSION_METHOD_BZIP2, file_object=os_file_object)
    file_object.open()

    self.assertEquals(file_object.get_size(), 1247)

    file_object.close()
    os_file_object.close()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = compressed_stream.CompressedStream()
    file_object.open(self._compressed_stream_path_spec)

    self.assertEquals(file_object.get_size(), 1247)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = compressed_stream.CompressedStream()
    file_object.open(self._compressed_stream_path_spec)

    file_object.seek(167 + 10)
    self.assertEquals(file_object.read(5), '53:01')
    self.assertEquals(file_object.get_offset(), 167 + 15)

    file_object.seek(-10, os.SEEK_END)
    self.assertEquals(file_object.read(5), 'times')

    file_object.seek(2, os.SEEK_CUR)
    self.assertEquals(file_object.read(2), '--')

    # Conforming to the POSIX seek the offset can exceed the file size
    # but reading will result in no data being returned.
    file_object.seek(2000, os.SEEK_SET)
    self.assertEquals(file_object.get_offset(), 2000)
    self.assertEquals(file_object.read(2), '')

    with self.assertRaises(IOError):
      file_object.seek(-10, os.SEEK_SET)

    # On error the offset should not change.
    self.assertEquals(file_object.get_offset(), 2000)

    with self.assertRaises(IOError):
      file_object.seek(10, 5)

    # On error the offset should not change.
    self.assertEquals(file_object.get_offset(), 2000)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = compressed_stream.CompressedStream()
    file_object.open(self._compressed_stream_path_spec)

    file_object.seek(167, os.SEEK_SET)

    self.assertEquals(file_object.get_offset(), 167)

    expected_buffer = (
        'Jan 22 07:53:01 myhostname.myhost.com CRON[31051]: (root) CMD '
        '(touch /var/run/crond.somecheck)\n')

    read_buffer = file_object.read(95)

    self.assertEquals(read_buffer, expected_buffer)

    self.assertEquals(file_object.get_offset(), 167 + 95)

    file_object.close()


if __name__ == '__main__':
  unittest.main()
