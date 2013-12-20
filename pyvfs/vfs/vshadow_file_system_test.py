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
"""Tests for a file system implementation on top of Volume Shadow Snapshots."""

import os
import unittest

import pyvshadow

from pyvfs.file_io import qcow_file_io
from pyvfs.path import os_path_spec
from pyvfs.path import qcow_path_spec
from pyvfs.path import vshadow_path_spec
from pyvfs.vfs import vshadow_file_system


class VShadowFileSystemTest(unittest.TestCase):
  """The unit test for a file system object on top of VSS."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = os.path.join('test_data', 'vsstest.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QcowPathSpec(parent=path_spec)
    self._qcow_file_object = qcow_file_io.QcowFile()
    self._qcow_file_object.open(self._qcow_path_spec)

  def testIntialize(self):
    """Test the initialize functionality."""
    vshadow_volume = pyvshadow.volume()
    vshadow_volume.open_file_object(self._qcow_file_object)
    file_system = vshadow_file_system.VShadowFileSystem(
        vshadow_volume, self._qcow_path_spec)

    self.assertNotEquals(file_system, None)

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    vshadow_volume = pyvshadow.volume()
    vshadow_volume.open_file_object(self._qcow_file_object)
    file_system = vshadow_file_system.VShadowFileSystem(
        vshadow_volume, self._qcow_path_spec)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._qcow_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=9, parent=self._qcow_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

  def testGetFileEntryByPathSpec(self):
    """Test the get entry by path specification functionality."""
    vshadow_volume = pyvshadow.volume()
    vshadow_volume.open_file_object(self._qcow_file_object)
    file_system = vshadow_file_system.VShadowFileSystem(
        vshadow_volume, self._qcow_path_spec)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._qcow_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)
    self.assertEquals(file_entry.name, u'vss2')

    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=9, parent=self._qcow_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertEquals(file_entry, None)

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    vshadow_volume = pyvshadow.volume()
    vshadow_volume.open_file_object(self._qcow_file_object)
    file_system = vshadow_file_system.VShadowFileSystem(
        vshadow_volume, self._qcow_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertNotEquals(file_entry, None)
    self.assertEquals(file_entry.name, u'')


if __name__ == '__main__':
  unittest.main()
