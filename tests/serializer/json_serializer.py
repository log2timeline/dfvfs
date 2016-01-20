#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the serializer object implementation using JSON."""

import json
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

    test_path = os.path.abspath(test_file)

    self._json_dict = {
        u'__type__': u'PathSpec',
        u'type_indicator': u'TSK',
        u'location': u'/a_directory/another_file',
        u'inode': 16,
        u'parent': {
            u'__type__': u'PathSpec',
            u'type_indicator': u'VSHADOW',
            u'store_index': 1,
            u'parent': {
                u'__type__': u'PathSpec',
                u'type_indicator': u'QCOW',
                u'parent': {
                    u'__type__': u'PathSpec',
                    u'type_indicator': u'OS',
                    u'location': test_path
                }
            }
        }
    }

  def testReadSerialized(self):
    """Test the read serialized functionality."""
    # We use json.dumps to make sure the dict does not serialize into
    # an invalid JSON string e.g. one that contains string prefixes
    # like b'' or u''.
    serialized = json.dumps(self._json_dict)
    path_spec = serializer.JsonPathSpecSerializer.ReadSerialized(serialized)
    self.assertEqual(path_spec.comparable, self._tsk_path_spec.comparable)

  def testWriteSerialized(self):
    """Test the write serialized functionality."""
    serialized = serializer.JsonPathSpecSerializer.WriteSerialized(
        self._tsk_path_spec)

    # We use json.loads here to compare dicts since we cannot pre-determine
    # the actual order of values in the JSON string.
    json_dict = json.loads(serialized)
    self.assertEqual(json_dict, self._json_dict)


if __name__ == '__main__':
  unittest.main()
