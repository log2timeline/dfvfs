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
"""This file contains the unit tests for the data range file-like object."""

import os
import unittest

from pyvfs.io import data_range


class DataRange(unittest.TestCase):
  """The unit test for the data range file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._test_file = os.path.join('test_data', 'syslog_copy')

  def testOpenClose(self):
    """Test the open and close functionality."""
    file_object = data_range.DataRange()

    file_object.open(self._test_file)

    file_object.close()

  def testSetRange(self):
    """Test the read functionality."""
    file_object = data_range.DataRange()

    file_object.open(self._test_file)
    file_object.SetRange(167, 1080)

    self.assertEquals(file_object.get_size(), 1080)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = data_range.DataRange()

    file_object.open(self._test_file)
    file_object.SetRange(167, 1080)

    expected_buffer = (
        'Jan 22 07:53:01 myhostname.myhost.com CRON[31051]: (root) CMD '
        '(touch /var/run/crond.somecheck)\n')

    read_buffer = file_object.read(95)

    self.assertEquals(read_buffer, expected_buffer)

    file_object.close()


if __name__ == '__main__':
  unittest.main()
