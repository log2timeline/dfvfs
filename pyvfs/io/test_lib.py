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
"""Shared test cases."""

import os
import unittest


class SylogTestCase(unittest.TestCase):
  """The unit test case for the syslog test data."""

  def _testGetSizeFileObject(self, file_object):
    """Runs the get size tests on the file-like object.
  
    Args:
      file_object: the file-like object with the test data.
    """
    self.assertEquals(file_object.get_size(), 1247)

  def _testSeekFileObject(self, file_object, base_offset=167):
    """Runs the seek tests on the file-like object.
  
    Args:
      file_object: the file-like object with the test data.
      base_offset: optional base offset use in the tests, the default is 167.
    """
    file_object.seek(base_offset + 10)
    self.assertEquals(file_object.read(5), '53:01')

    expected_offset = base_offset + 15
    self.assertEquals(file_object.get_offset(), expected_offset)
  
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
  
  def _testReadFileObject(self, file_object, base_offset=167):
    """Runs the read tests on the file-like object.
  
    Args:
      file_object: the file-like object with the test data.
      base_offset: optional base offset use in the tests, the default is 167.
    """
    file_object.seek(base_offset, os.SEEK_SET)
  
    self.assertEquals(file_object.get_offset(), base_offset)
  
    expected_buffer = (
        'Jan 22 07:53:01 myhostname.myhost.com CRON[31051]: (root) CMD '
        '(touch /var/run/crond.somecheck)\n')
  
    read_buffer = file_object.read(95)
  
    self.assertEquals(read_buffer, expected_buffer)

    expected_offset = base_offset + 95

    self.assertEquals(file_object.get_offset(), expected_offset)
