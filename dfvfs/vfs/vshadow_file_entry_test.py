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
"""Tests for the file entry implementation using the pyvshadow."""

import os
import unittest

import pyvshadow

from dfvfs.file_io import qcow_file_io
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import vshadow_path_spec
from dfvfs.vfs import vshadow_file_entry
from dfvfs.vfs import vshadow_file_system


class VShadowFileEntryTest(unittest.TestCase):
  """The unit test for the VSS file entry object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = os.path.join('test_data', 'vsstest.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QcowPathSpec(parent=path_spec)
    file_object = qcow_file_io.QcowFile()
    file_object.open(self._qcow_path_spec)
    vshadow_volume = pyvshadow.volume()
    vshadow_volume.open_file_object(file_object)
    self._vshadow_file_system = vshadow_file_system.VShadowFileSystem(
        vshadow_volume, self._qcow_path_spec)

  # qcowmount test_data/vsstest.qcow2 fuse/
  # vshadowinfo fuse/qcow1
  #
  # Volume Shadow Snapshot information:
  #   Number of stores:	2
  #
  # Store: 1
  #   ...
  #   Identifier		: 600f0b69-5bdf-11e3-9d6c-005056c00008
  #   Shadow copy set ID	: 0a4e3901-6abb-48fc-95c2-6ab9e38e9e71
  #   Creation time		: Dec 03, 2013 06:35:09.736378700 UTC
  #   Shadow copy ID		: 4e3c03c2-7bc6-4288-ad96-c1eac1a55f71
  #   Volume size		: 1073741824 bytes
  #   Attribute flags		: 0x00420009
  #
  # Store: 2
  #   Identifier		: 600f0b6d-5bdf-11e3-9d6c-005056c00008
  #   Shadow copy set ID	: 8438a0ee-0f06-443b-ac0c-2905647ca5d6
  #   Creation time		: Dec 03, 2013 06:37:48.919058300 UTC
  #   Shadow copy ID		: 18f1ac6e-959d-436f-bdcc-e797a729e290
  #   Volume size		: 1073741824 bytes
  #   Attribute flags		: 0x00420009

  def testIntialize(self):
    """Test the initialize functionality."""
    file_entry = vshadow_file_entry.VShadowFileEntry(
        self._vshadow_file_system, self._qcow_path_spec)

    self.assertNotEquals(file_entry, None)

  def testGetParentFileEntry(self):
    """Test the get parent file entry functionality."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._qcow_path_spec)
    file_entry = self._vshadow_file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertEquals(parent_file_entry, None)

  def testGetStat(self):
    """Test the get stat functionality."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._qcow_path_spec)
    file_entry = self._vshadow_file_system.GetFileEntryByPathSpec(path_spec)

    stat_object = file_entry.GetStat()

    self.assertNotEquals(stat_object, None)
    self.assertEquals(stat_object.type, stat_object.TYPE_FILE)

  def testIsFunctions(self):
    """Test the Is? functionality."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._qcow_path_spec)
    file_entry = self._vshadow_file_system.GetFileEntryByPathSpec(path_spec)

    self.assertFalse(file_entry.IsRoot())
    self.assertFalse(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertFalse(file_entry.IsDirectory())
    self.assertTrue(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/', parent=self._qcow_path_spec)
    file_entry = self._vshadow_file_system.GetFileEntryByPathSpec(path_spec)

    self.assertTrue(file_entry.IsRoot())
    self.assertTrue(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertTrue(file_entry.IsDirectory())
    self.assertFalse(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

  def testSubFileEntries(self):
    """Test the sub file entries iteration functionality."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/', parent=self._qcow_path_spec)
    file_entry = self._vshadow_file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)

    expected_sub_file_entry_names = [u'vss1', u'vss2']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEquals(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEquals(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))


if __name__ == '__main__':
  unittest.main()
