#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The dfVFS Project Authors.
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
"""Tests for the file-like object implementation using pyqcow."""

import os
import unittest

from dfvfs.file_io import test_lib
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec


class QcowFileTest(test_lib.ImageFileTestCase):
  """The unit test for the QCOW image file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = os.path.join('test_data', 'image.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QcowPathSpec(parent=path_spec)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._testOpenCloseInode(self._qcow_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._testOpenCloseLocation(self._qcow_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._testSeek(self._qcow_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._testRead(self._qcow_path_spec)


if __name__ == '__main__':
  unittest.main()
