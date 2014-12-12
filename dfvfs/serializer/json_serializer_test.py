#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 The dfVFS Project Authors.
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
"""Tests for the serializer object implementation using JSON."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import tsk_path_spec
from dfvfs.path import vshadow_path_spec
from dfvfs.serializer import json_serializer as serializer


class JsonPathSpecSerializerTest(unittest.TestCase):
  """Tests for the JSON path specification serializer object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = os.path.join('test_data', 'image.qcow2')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QcowPathSpec(
        parent=self._os_path_spec)
    self._vshadow_path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._qcow_path_spec)
    self._tsk_path_spec = tsk_path_spec.TSKPathSpec(
        inode=16, location='/a_directory/another_file',
        parent=self._vshadow_path_spec)

    test_path = os.path.abspath(test_file).encode('utf8')
    test_path_length = len(test_path)

    if test_path_length < 228:
      self._json_string = (
          '{{"type_indicator": "TSK", "inode": 16, "location": '
          '"/a_directory/another_file", "parent": "{{\\"store_index\\": 1, '
          '\\"type_indicator\\": \\"VSHADOW\\", \\"parent\\": '
          '\\"{{\\\\\\"type_indicator\\\\\\": \\\\\\"QCOW\\\\\\", '
          '\\\\\\"parent\\\\\\": \\\\\\"{{\\\\\\\\\\\\\\"type_indicator'
          '\\\\\\\\\\\\\\": \\\\\\\\\\\\\\"OS\\\\\\\\\\\\\\", \\\\\\\\\\\\\\'
          '"location\\\\\\\\\\\\\\": \\\\\\\\\\\\\\"{0:s}\\\\\\\\\\\\\\"}}'
          '\\\\\\"}}\\"}}"}}').format(test_path)

  def testReadSerialized(self):
    """Test the read serialized functionality."""
    if self._json_string:
      path_spec = serializer.JsonPathSpecSerializer.ReadSerialized(
          self._json_string)
      self.assertEquals(path_spec.comparable, self._tsk_path_spec.comparable)

  def testWriteSerialized(self):
    """Test the write serialized functionality."""
    if self._json_string:
      serialized = serializer.JsonPathSpecSerializer.WriteSerialized(
          self._tsk_path_spec)

      self.assertEquals(serialized, self._json_string)


if __name__ == '__main__':
  unittest.main()
