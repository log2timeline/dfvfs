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
"""Tests for the file entry implementation using the pyvshadow."""

import os
import unittest

import pyvshadow

from pyvfs.io import qcow_file_io
from pyvfs.path import os_path_spec
from pyvfs.path import qcow_path_spec
from pyvfs.path import vshadow_path_spec
from pyvfs.vfs import vshadow_file_entry
from pyvfs.vfs import vshadow_file_system


class VShadowFileEntryTest(unittest.TestCase):
  """The unit test for the VSS file entry object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = os.path.join('test_data', 'vsstest.qcow2')
    path_spec = os_path_spec.OSPathSpec(test_file)
    self._qcow_path_spec = qcow_path_spec.QcowPathSpec(path_spec)
    file_object = qcow_file_io.QcowFile()
    file_object.open(self._qcow_path_spec)
    vshadow_volume = pyvshadow.volume()
    vshadow_volume.open_file_object(file_object)
    self._vshadow_file_system = vshadow_file_system.VShadowFileSystem(
        vshadow_volume, self._qcow_path_spec)

  def testIntialize(self):
    """Test the initialize functionality."""
    file_entry = vshadow_file_entry.VShadowFileEntry(
        self._vshadow_file_system, self._qcow_path_spec)

    self.assertNotEquals(file_entry, None)

  def testSubFileEntries(self):
    """Test the sub file entries iteration functionality."""
    path_spec = vshadow_path_spec.VShadowPathSpec(None, self._qcow_path_spec)
    file_entry = self._vshadow_file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)

    expected_sub_file_entry_names = ['vss1', 'vss2']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEquals(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEquals(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))


if __name__ == '__main__':
  unittest.main()
