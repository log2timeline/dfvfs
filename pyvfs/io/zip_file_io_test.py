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
"""Tests for the zip extracted file-like object."""

import os
import unittest

from pyvfs.io import zip_file_io
from pyvfs.io import test_lib
from pyvfs.path import os_path_spec
from pyvfs.path import zip_path_spec


class ZipFileTest(test_lib.SylogTestCase):
  """The unit test for a zip extracted file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    location = os.path.join('test_data', 'syslog.zip')
    path_spec = os_path_spec.OSPathSpec(location)
    self._zip_path_spec = zip_path_spec.ZipPathSpec(
        '/syslog', path_spec)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = zip_file_io.ZipFile()
    file_object.open(self._zip_path_spec)

    self._testGetSizeFileObject(file_object)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = zip_file_io.ZipFile()
    file_object.open(self._zip_path_spec)

    self._testSeekFileObject(file_object)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = zip_file_io.ZipFile()
    file_object.open(self._zip_path_spec)

    self._testReadFileObject(file_object)

    file_object.close()


if __name__ == '__main__':
  unittest.main()
