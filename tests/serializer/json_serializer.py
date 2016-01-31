#!/usr/bin/python
# -*- coding: utf-8 -*-
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

  maxDiff = None

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = os.path.join(u'test_data', u'image.qcow2')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(
        parent=self._os_path_spec)
    self._vshadow_path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._qcow_path_spec)
    self._tsk_path_spec = tsk_path_spec.TSKPathSpec(
        inode=16, location=u'/a_directory/another_file',
        parent=self._vshadow_path_spec)

    self._tsk_path_spec_dict = {
        u'inode': 16,
        u'location': u'/a_directory/another_file',
        u'parent': {
            u'store_index': 1,
            u'parent': {
                u'parent': {
                    u'location': os.path.abspath(test_file)}
            }
        }
    }

  def testReadAndWriteSerialized(self):
    """Test the ReadSerialized and WriteSerialized function."""
    serialized_path_spec = serializer.JsonPathSpecSerializer.WriteSerialized(
        self._tsk_path_spec)

    self.assertIsNotNone(serialized_path_spec)

    path_spec = serializer.JsonPathSpecSerializer.ReadSerialized(
        serialized_path_spec)

    self.assertIsNotNone(path_spec)

    path_spec_dict = path_spec.CopyToDict()
    self.assertEqual(
        sorted(path_spec_dict.items()),
        sorted(self._tsk_path_spec_dict.items()))


if __name__ == '__main__':
  unittest.main()
