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
    self._qcow_path_spec = qcow_path_spec.QcowPathSpec(
        parent=self._os_path_spec)
    self._vshadow_path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._qcow_path_spec)
    self._tsk_path_spec = tsk_path_spec.TSKPathSpec(
        inode=16, location=u'/a_directory/another_file',
        parent=self._vshadow_path_spec)

    test_path = os.path.abspath(test_file).encode(u'utf8')

    # Do not use u'' or b'' we need native string objects here
    # otherwise the strings will be formatted with a prefix and
    # are not a valid JSON string.
    self._json_dict = {
        '__type__': 'PathSpec',
        'type_indicator': 'TSK',
        'location': '/a_directory/another_file',
        'inode': 16,
        'parent': {
            '__type__': 'PathSpec',
            'type_indicator': 'VSHADOW',
            'store_index': 1,
            'parent': {
                '__type__': 'PathSpec',
                'type_indicator': 'QCOW',
                'parent': {
                    '__type__': 'PathSpec',
                    'type_indicator': 'OS',
                    'location': test_path
                }
            }
        }
    }

  def testReadSerialized(self):
    """Test the read serialized functionality."""
    serialized = u'{0!s}'.format(self._json_dict).replace(u'\'', u'"')
    path_spec = serializer.JsonPathSpecSerializer.ReadSerialized(serialized)
    self.assertEquals(path_spec.comparable, self._tsk_path_spec.comparable)

  def testWriteSerialized(self):
    """Test the write serialized functionality."""
    serialized = serializer.JsonPathSpecSerializer.WriteSerialized(
        self._tsk_path_spec)

    # We need to compare dicts since we cannot determine the order
    # of values in the string.
    json_dict = json.loads(serialized)
    self.assertEquals(json_dict, self._json_dict)


if __name__ == '__main__':
  unittest.main()
