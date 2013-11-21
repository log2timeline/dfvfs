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
"""Tests for the file entry implementation using the SleuthKit (TSK)."""

import os
import unittest

from pyvfs.io import os_file
from pyvfs.path import os_path_spec
from pyvfs.path import tsk_path_spec
from pyvfs.vfs import tsk_file_system


class TSKFileEntryTest(unittest.TestCase):
  """The unit test for the SleuthKit (TSK) file entry object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = os.path.join('test_data', 'image.dd')
    path_spec = os_path_spec.OSPathSpec(test_file)
    file_object = os_file.OSFile()
    file_object.open(path_spec, mode='rb')
    self.file_system = tsk_file_system.TSKFileSystem(file_object)

  def testGetFileEntryByPathSpec(self):
    """Test the open and close functionality."""
    path_spec = tsk_path_spec.TSKPathSpec(inode=15)
    file_entry = self.file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)
    # TODO: add tests.


if __name__ == '__main__':
  unittest.main()
