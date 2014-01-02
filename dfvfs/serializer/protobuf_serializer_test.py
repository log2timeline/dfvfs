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
"""Tests for the serializer object implementation using protobuf."""

import platform
import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import tsk_path_spec
from dfvfs.path import vshadow_path_spec
from dfvfs.proto import transmission_pb2
from dfvfs.serializer import protobuf_serializer as serializer


class ProtobufPathSpecSerializerTest(unittest.TestCase):
  """The unit test for the SleuthKit (TSK) file-like object."""

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

    if platform.system() == 'Windows':
      self._proto_string = (
          '\n0\n#\n\x1b'
          '\x12\x02OS2\x15test_data\\image.qcow2'
          '\x12\x04QCOW'
          '\x12\x07VSHADOWX\x01'
          '\x12\x03TSK(\x102\x19/a_directory/another_file')
    else:
      self._proto_string = (
          '\n0\n#\n\x1b'
          '\x12\x02OS2\x15test_data/image.qcow2'
          '\x12\x04QCOW'
          '\x12\x07VSHADOWX\x01'
          '\x12\x03TSK(\x102\x19/a_directory/another_file')

    self._proto = transmission_pb2.PathSpec()
    self._proto.ParseFromString(self._proto_string)

  def testReadSerialized(self):
    """Test the read serialized functionality."""
    path_spec = serializer.ProtobufPathSpecSerializer.ReadSerialized(
        self._proto)
    self.assertEquals(path_spec.comparable, self._tsk_path_spec.comparable)

  def testWriteSerialized(self):
    """Test the write serialized functionality."""
    serialized = serializer.ProtobufPathSpecSerializer.WriteSerialized(
        self._tsk_path_spec)
    self.assertEquals(serialized, self._proto)


if __name__ == '__main__':
  unittest.main()
