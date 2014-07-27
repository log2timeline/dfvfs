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
"""Tests for the source scanner object."""

import os
import unittest

from dfvfs.helpers import source_scanner
from dfvfs.lib import definitions
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import vshadow_path_spec
from dfvfs.resolver import resolver


class SourceScannerTest(unittest.TestCase):
  """The unit test for the source scanner object."""

  _BDE_PASSWORD = 'bde-TEST'

  maxDiff = None

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._source_scanner = source_scanner.SourceScanner()

  def testScan(self):
    """Test the Scan() function."""
    test_file = os.path.join('test_data', 'tsk_volume_system.raw')
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    scan_context = self._source_scanner.Scan(scan_context)
    self.assertNotEquals(scan_context, None)
    self.assertEquals(
        scan_context.source_type, scan_context.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)
    self.assertNotEquals(scan_context.last_scan_node, None)
    self.assertNotEquals(scan_context.last_scan_node.path_spec, None)
    self.assertEquals(
        scan_context.last_scan_node.type_indicator,
        definitions.TYPE_INDICATOR_TSK_PARTITION)

    self.assertEquals(len(scan_context.last_scan_node.sub_nodes), 7)

    # We need to use the path specificiation provided by the scanner
    # since the scanner does not support scanning for sub path specifications
    # it does not know about. The scan path spec is manually defined as:
    # scan_path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
    #     location=u'/p2', part_index=6, start_offset=0x0002c000,
    #     parent=scan_context.last_scan_node.path_spec.parent)

    scan_path_spec = scan_context.last_scan_node.sub_nodes[6].path_spec

    scan_context = self._source_scanner.Scan(
        scan_context, scan_path_spec=scan_path_spec)
    self.assertNotEquals(scan_context, None)
    self.assertEquals(
        scan_context.source_type, scan_context.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)
    self.assertNotEquals(scan_context.last_scan_node, None)
    self.assertNotEquals(scan_context.last_scan_node.path_spec, None)
    self.assertEquals(
        scan_context.last_scan_node.type_indicator,
        definitions.TYPE_INDICATOR_TSK)

    test_file = os.path.join('test_data', 'vsstest.qcow2')
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    scan_context = self._source_scanner.Scan(scan_context)
    self.assertNotEquals(scan_context, None)
    self.assertEquals(
        scan_context.source_type, scan_context.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)
    self.assertNotEquals(scan_context.last_scan_node, None)
    self.assertNotEquals(scan_context.last_scan_node.path_spec, None)
    self.assertEquals(
        scan_context.last_scan_node.type_indicator,
        definitions.TYPE_INDICATOR_VSHADOW)

    self.assertEquals(len(scan_context.last_scan_node.sub_nodes), 3)

    # We need to use the path specificiation provided by the scanner
    # since the scanner does not support scanning for sub path specifications
    # it does not know about. The scan path spec is manually defined as:
    # scan_path_spec = vshadow_path_spec.VShadowPathSpec(
    #     location=u'/vss1', store_index=0,
    #     parent=scan_context.last_scan_node.path_spec.parent)

    scan_path_spec = scan_context.last_scan_node.sub_nodes[1].path_spec

    scan_context = self._source_scanner.Scan(
        scan_context, scan_path_spec=scan_path_spec)
    self.assertNotEquals(scan_context, None)
    self.assertEquals(
        scan_context.source_type, scan_context.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)
    self.assertNotEquals(scan_context.last_scan_node, None)
    self.assertNotEquals(scan_context.last_scan_node.path_spec, None)
    self.assertEquals(
        scan_context.last_scan_node.type_indicator,
        definitions.TYPE_INDICATOR_TSK)

    test_file = os.path.join('test_data', 'bdetogo.raw')
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    scan_context = self._source_scanner.Scan(scan_context)
    self.assertNotEquals(scan_context, None)
    self.assertEquals(
        scan_context.source_type, scan_context.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)
    self.assertNotEquals(scan_context.last_scan_node, None)
    self.assertNotEquals(scan_context.last_scan_node.path_spec, None)
    self.assertEquals(
        scan_context.last_scan_node.type_indicator,
        definitions.TYPE_INDICATOR_BDE)

    resolver.Resolver.key_chain.SetCredential(
        scan_context.last_scan_node.path_spec, u'password', self._BDE_PASSWORD)

    scan_context = self._source_scanner.Scan(scan_context)
    self.assertNotEquals(scan_context, None)
    self.assertEquals(
        scan_context.source_type, scan_context.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)
    self.assertNotEquals(scan_context.last_scan_node, None)
    self.assertNotEquals(scan_context.last_scan_node.path_spec, None)
    self.assertEquals(
        scan_context.last_scan_node.type_indicator,
        definitions.TYPE_INDICATOR_TSK)

    test_file = os.path.join('test_data', 'testdir_os')
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    scan_context = self._source_scanner.Scan(scan_context)
    self.assertNotEquals(scan_context, None)
    self.assertEquals(
        scan_context.source_type, scan_context.SOURCE_TYPE_DIRECTORY)
    self.assertNotEquals(scan_context.last_scan_node, None)
    self.assertNotEquals(scan_context.last_scan_node.path_spec, None)
    self.assertEquals(
        scan_context.last_scan_node.type_indicator,
        definitions.TYPE_INDICATOR_OS)

    test_file = os.path.join('test_data', 'testdir_os', 'file1.txt')
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    scan_context = self._source_scanner.Scan(scan_context)
    self.assertNotEquals(scan_context, None)
    self.assertEquals(
        scan_context.source_type, scan_context.SOURCE_TYPE_FILE)
    self.assertNotEquals(scan_context.last_scan_node, None)
    self.assertNotEquals(scan_context.last_scan_node.path_spec, None)
    self.assertEquals(
        scan_context.last_scan_node.type_indicator,
        definitions.TYPE_INDICATOR_OS)

  def testScanForFileSystem(self):
    """Test the ScanForFileSystem() function."""
    test_file = os.path.join('test_data', 'vsstest.qcow2')
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)
    source_path_spec = qcow_path_spec.QcowPathSpec(parent=source_path_spec)
    source_path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=source_path_spec)

    path_spec = self._source_scanner.ScanForFileSystem(source_path_spec)
    self.assertNotEquals(path_spec, None)
    self.assertEquals(path_spec.type_indicator, definitions.TYPE_INDICATOR_TSK)

    test_file = os.path.join('test_data', 'mactime.body')
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForFileSystem(source_path_spec)
    self.assertEquals(path_spec, None)

  def testScanForStorageMediaImage(self):
    """Test the ScanForStorageMediaImage() function."""
    test_file = os.path.join('test_data', 'image.dd')
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForStorageMediaImage(source_path_spec)
    self.assertNotEquals(path_spec, None)
    self.assertEquals(path_spec.type_indicator, definitions.TYPE_INDICATOR_RAW)

    test_file = os.path.join('test_data', 'image.raw.000')
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForStorageMediaImage(source_path_spec)
    self.assertNotEquals(path_spec, None)
    self.assertEquals(path_spec.type_indicator, definitions.TYPE_INDICATOR_RAW)

    test_file = os.path.join('test_data', 'image.E01')
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForStorageMediaImage(source_path_spec)
    self.assertNotEquals(path_spec, None)
    self.assertEquals(path_spec.type_indicator, definitions.TYPE_INDICATOR_EWF)

    test_file = os.path.join('test_data', 'image.qcow2')
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForStorageMediaImage(source_path_spec)
    self.assertNotEquals(path_spec, None)
    self.assertEquals(
        path_spec.type_indicator, definitions.TYPE_INDICATOR_QCOW)

    test_file = os.path.join('test_data', 'image.vhd')
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForStorageMediaImage(source_path_spec)
    self.assertNotEquals(path_spec, None)
    self.assertEquals(
        path_spec.type_indicator, definitions.TYPE_INDICATOR_VHDI)

    test_file = os.path.join('test_data', 'image.vmdk')
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForStorageMediaImage(source_path_spec)
    self.assertNotEquals(path_spec, None)
    self.assertEquals(
        path_spec.type_indicator, definitions.TYPE_INDICATOR_VMDK)

    test_file = os.path.join('test_data', 'mactime.body')
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForStorageMediaImage(source_path_spec)
    self.assertEquals(path_spec, None)

  def testScanForVolumeSystem(self):
    """Test the ScanForVolumeSystem() function."""
    test_file = os.path.join('test_data', 'tsk_volume_system.raw')
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForVolumeSystem(source_path_spec)
    self.assertNotEquals(path_spec, None)
    self.assertEquals(
        path_spec.type_indicator, definitions.TYPE_INDICATOR_TSK_PARTITION)

    test_file = os.path.join('test_data', 'vsstest.qcow2')
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)
    source_path_spec = qcow_path_spec.QcowPathSpec(parent=source_path_spec)

    path_spec = self._source_scanner.ScanForVolumeSystem(source_path_spec)
    self.assertNotEquals(path_spec, None)
    self.assertEquals(
        path_spec.type_indicator, definitions.TYPE_INDICATOR_VSHADOW)

    test_file = os.path.join('test_data', 'bdetogo.raw')
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForVolumeSystem(source_path_spec)
    self.assertNotEquals(path_spec, None)
    self.assertEquals(path_spec.type_indicator, definitions.TYPE_INDICATOR_BDE)

    test_file = os.path.join('test_data', 'mactime.body')
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForVolumeSystem(source_path_spec)
    self.assertEquals(path_spec, None)


if __name__ == '__main__':
  unittest.main()
