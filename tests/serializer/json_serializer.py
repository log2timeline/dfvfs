#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the serializer object implementation using JSON."""

from __future__ import unicode_literals

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import tsk_path_spec
from dfvfs.path import vshadow_path_spec
from dfvfs.serializer import json_serializer as serializer

from tests import test_lib as shared_test_lib


class JsonPathSpecSerializerTest(shared_test_lib.BaseTestCase):
  """Tests for the JSON path specification serializer."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = self._GetTestFilePath(['ext2.qcow2'])
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(
        parent=self._os_path_spec)
    self._vshadow_path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._qcow_path_spec)
    self._tsk_path_spec = tsk_path_spec.TSKPathSpec(
        inode=16, location='/a_directory/another_file',
        parent=self._vshadow_path_spec)

    self._tsk_path_spec_dict = {
        'inode': 16,
        'location': '/a_directory/another_file',
        'parent': {
            'store_index': 1,
            'parent': {
                'parent': {
                    'location': os.path.abspath(test_file)}
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
