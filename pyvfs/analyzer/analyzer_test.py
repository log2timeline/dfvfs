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
"""Tests for the Virtual File System (VFS) format analyzer."""

import unittest
import os

from pyvfs.analyzer import analyzer
from pyvfs.lib import definitions
from pyvfs.path import os_path_spec
from pyvfs.path import qcow_path_spec
from pyvfs.path import vshadow_path_spec


class AnalyzerTest(unittest.TestCase):
  """Class to test the analyzer."""

  def testGetStorageMediaImageTypeIndicators(self):
    """Function to test the get image type indicators function."""
    test_file = os.path.join('test_data', 'image.E01')
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_EWF]
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEquals(type_indicators, expected_type_indicators)

    test_file = os.path.join('test_data', 'image.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_QCOW]
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEquals(type_indicators, expected_type_indicators)

    test_file = os.path.join('test_data', 'image.vhd')
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_VHDI]
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEquals(type_indicators, expected_type_indicators)

  def testGetVolumeSystemTypeIndicators(self):
    """Function to test the get volume system type indicators function."""
    test_file = os.path.join('test_data', 'tsk_volume_system.raw')
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_TSK_PARTITION]
    type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
        path_spec)
    self.assertEquals(type_indicators, expected_type_indicators)

    test_file = os.path.join('test_data', 'vsstest.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = qcow_path_spec.QcowPathSpec(parent=path_spec)

    expected_type_indicators = [definitions.TYPE_INDICATOR_VSHADOW]
    type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
        path_spec)
    self.assertEquals(type_indicators, expected_type_indicators)

  def testGetFileSystemTypeIndicators(self):
    """Function to test the get file system type indicators function."""
    test_file = os.path.join('test_data', 'vsstest.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = qcow_path_spec.QcowPathSpec(parent=path_spec)
    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=path_spec)

    expected_type_indicators = [definitions.TYPE_INDICATOR_TSK]
    type_indicators = analyzer.Analyzer.GetFileSystemTypeIndicators(
        path_spec)
    self.assertEquals(type_indicators, expected_type_indicators)


if __name__ == '__main__':
  unittest.main()
