#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the source scanner object."""

import unittest

from dfvfs.helpers import source_scanner
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import vshadow_path_spec

from tests import test_lib as shared_test_lib


class SourceScannerTest(shared_test_lib.BaseTestCase):
  """The unit test for the source scanner object."""

  _BDE_PASSWORD = u'bde-TEST'

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._source_scanner = source_scanner.SourceScanner()

  def _GetTestScanNode(self, scan_context):
    """Retrieves the scan node for testing.

    Retrieves the first scan node, from the root upwards, with more or less
    than 1 sub node.

    Args:
      scan_context (ScanContext): scan context.

    Returns:
      SourceScanNode: scan node.
    """
    scan_node = scan_context.GetRootScanNode()
    while len(scan_node.sub_nodes) == 1:
      scan_node = scan_node.sub_nodes[0]

    return scan_node

  @shared_test_lib.skipUnlessHasTestFile([u'tsk_volume_system.raw'])
  def testScanPartitionedImage(self):
    """Test the Scan() function on a partitioned image."""
    test_file = self._GetTestFilePath([u'tsk_volume_system.raw'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    self._source_scanner.Scan(scan_context)
    self.assertEqual(
        scan_context.source_type, definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)

    scan_node = self._GetTestScanNode(scan_context)
    self.assertIsNotNone(scan_node)
    self.assertEqual(
        scan_node.type_indicator, definitions.TYPE_INDICATOR_TSK_PARTITION)

    self.assertEqual(len(scan_node.sub_nodes), 7)

    # TODO: use GetSubNodeByLocation
    for scan_node in scan_node.sub_nodes[6].sub_nodes:
      if getattr(scan_node.path_spec, u'location', None) == u'/':
        break

    self.assertEqual(scan_node.type_indicator, definitions.TYPE_INDICATOR_TSK)

  @shared_test_lib.skipUnlessHasTestFile([u'vsstest.qcow2'])
  def testScanVSS(self):
    """Test the Scan() function on VSS."""
    test_file = self._GetTestFilePath([u'vsstest.qcow2'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    self._source_scanner.Scan(scan_context)
    self.assertEqual(
        scan_context.source_type, definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)

    scan_node = self._GetTestScanNode(scan_context)
    self.assertIsNotNone(scan_node)
    self.assertEqual(scan_node.type_indicator, definitions.TYPE_INDICATOR_QCOW)
    self.assertEqual(len(scan_node.sub_nodes), 2)

    scan_node = scan_node.sub_nodes[0]

    self.assertEqual(
        scan_node.type_indicator, definitions.TYPE_INDICATOR_VSHADOW)
    self.assertEqual(len(scan_node.sub_nodes), 2)

    scan_node = scan_node.sub_nodes[0]
    self.assertEqual(
        scan_node.type_indicator, definitions.TYPE_INDICATOR_VSHADOW)
    # By default the file system inside a VSS volume is not scanned.
    self.assertEqual(len(scan_node.sub_nodes), 0)

    self._source_scanner.Scan(scan_context, scan_path_spec=scan_node.path_spec)
    self.assertEqual(len(scan_node.sub_nodes), 1)

    for scan_node in scan_node.sub_nodes:
      if getattr(scan_node.path_spec, u'location', None) == u'/':
        break

    expected_type_indicator = definitions.PREFERRED_NTFS_BACK_END
    self.assertEqual(scan_node.type_indicator, expected_type_indicator)

  @shared_test_lib.skipUnlessHasTestFile([u'bdetogo.raw'])
  def testScanBDE(self):
    """Test the Scan() function on BDE."""
    test_file = self._GetTestFilePath([u'bdetogo.raw'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    self._source_scanner.Scan(scan_context)
    self.assertEqual(
        scan_context.source_type, definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)

    scan_node = self._GetTestScanNode(scan_context)
    self.assertIsNotNone(scan_node)
    self.assertEqual(scan_node.type_indicator, definitions.TYPE_INDICATOR_RAW)

    for scan_node in scan_node.sub_nodes:
      if getattr(scan_node.path_spec, u'location', None) is None:
        break

    self.assertIsNotNone(scan_node)
    self.assertEqual(scan_node.type_indicator, definitions.TYPE_INDICATOR_BDE)
    self.assertEqual(len(scan_node.sub_nodes), 0)

    self._source_scanner.Unlock(
        scan_context, scan_node.path_spec, u'password', self._BDE_PASSWORD)

    self._source_scanner.Scan(scan_context, scan_path_spec=scan_node.path_spec)
    self.assertEqual(len(scan_node.sub_nodes), 1)

    for scan_node in scan_node.sub_nodes:
      if getattr(scan_node.path_spec, u'location', None) == u'/':
        break

    self.assertIsNotNone(scan_node.path_spec)
    self.assertEqual(scan_node.type_indicator, definitions.TYPE_INDICATOR_TSK)

  @shared_test_lib.skipUnlessHasTestFile([u'testdir_os', u'file1.txt'])
  def testScanDirectory(self):
    """Test the Scan() function on a directory."""
    test_file = self._GetTestFilePath([u'testdir_os'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    self._source_scanner.Scan(scan_context)
    self.assertEqual(
        scan_context.source_type, definitions.SOURCE_TYPE_DIRECTORY)

    scan_node = self._GetTestScanNode(scan_context)
    self.assertIsNotNone(scan_node)
    self.assertIsNotNone(scan_node.path_spec)
    self.assertEqual(
        scan_node.type_indicator, definitions.TYPE_INDICATOR_OS)

    test_file = self._GetTestFilePath([u'testdir_os', u'file1.txt'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    self._source_scanner.Scan(scan_context)
    self.assertEqual(
        scan_context.source_type, definitions.SOURCE_TYPE_FILE)

    scan_node = self._GetTestScanNode(scan_context)
    self.assertIsNotNone(scan_node)
    self.assertIsNotNone(scan_node.path_spec)
    self.assertEqual(
        scan_node.type_indicator, definitions.TYPE_INDICATOR_OS)

  @shared_test_lib.skipUnlessHasTestFile([u'bogus.001'])
  def testScanFile(self):
    """Test the Scan() function on a file."""
    test_file = self._GetTestFilePath([u'bogus.001'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    self._source_scanner.Scan(scan_context)
    self.assertEqual(
        scan_context.source_type, definitions.SOURCE_TYPE_FILE)

    scan_node = self._GetTestScanNode(scan_context)
    self.assertIsNotNone(scan_node)
    self.assertIsNotNone(scan_node.path_spec)
    self.assertEqual(
        scan_node.type_indicator, definitions.TYPE_INDICATOR_OS)

  @shared_test_lib.skipUnlessHasTestFile([u'ímynd.dd'])
  def testScanRAW(self):
    """Test the Scan() function on a RAW image."""
    test_file = self._GetTestFilePath([u'ímynd.dd'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    self._source_scanner.Scan(scan_context)
    self.assertEqual(
        scan_context.source_type, definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)

    scan_node = self._GetTestScanNode(scan_context)
    self.assertIsNotNone(scan_node)
    self.assertIsNotNone(scan_node.path_spec)
    self.assertEqual(scan_node.type_indicator, definitions.TYPE_INDICATOR_TSK)

    self.assertEqual(len(scan_node.sub_nodes), 0)

  def testScanNonExisting(self):
    """Test the Scan() function."""
    test_file = self._GetTestFilePath([u'nosuchfile.raw'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    with self.assertRaises(errors.BackEndError):
      _ = self._source_scanner.Scan(scan_context)

  @shared_test_lib.skipUnlessHasTestFile([u'vsstest.qcow2'])
  def testScanForFileSystemVSS(self):
    """Test the ScanForFileSystem() function on VSS."""
    test_file = self._GetTestFilePath([u'vsstest.qcow2'])
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)
    source_path_spec = qcow_path_spec.QCOWPathSpec(parent=source_path_spec)
    source_path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=source_path_spec)

    path_spec = self._source_scanner.ScanForFileSystem(source_path_spec)
    self.assertIsNotNone(path_spec)

    expected_type_indicator = definitions.PREFERRED_NTFS_BACK_END
    self.assertEqual(path_spec.type_indicator, expected_type_indicator)

  @shared_test_lib.skipUnlessHasTestFile([u'vsstest.qcow2'])
  def testScanForFileSystemBodyFile(self):
    """Test the ScanForFileSystem() function on a body file."""
    test_file = self._GetTestFilePath([u'mactime.body'])
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForFileSystem(source_path_spec)
    self.assertIsNone(path_spec)

  @shared_test_lib.skipUnlessHasTestFile([u'ímynd.dd'])
  def testScanForStorageMediaImageRAW(self):
    """Test the ScanForStorageMediaImage() function on a RAW image."""
    test_file = self._GetTestFilePath([u'ímynd.dd'])
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForStorageMediaImage(source_path_spec)
    self.assertIsNotNone(path_spec)
    self.assertEqual(path_spec.type_indicator, definitions.TYPE_INDICATOR_RAW)

  @shared_test_lib.skipUnlessHasTestFile([u'image.raw.000'])
  def testScanForStorageMediaImageSplitRAW(self):
    """Test the ScanForStorageMediaImage() function on a split RAW image."""
    test_file = self._GetTestFilePath([u'image.raw.000'])
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForStorageMediaImage(source_path_spec)
    self.assertIsNotNone(path_spec)
    self.assertEqual(path_spec.type_indicator, definitions.TYPE_INDICATOR_RAW)

  @shared_test_lib.skipUnlessHasTestFile([u'image.E01'])
  def testScanForStorageMediaImageEWF(self):
    """Test the ScanForStorageMediaImage() function on an EWF image."""
    test_file = self._GetTestFilePath([u'image.E01'])
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForStorageMediaImage(source_path_spec)
    self.assertIsNotNone(path_spec)
    self.assertEqual(path_spec.type_indicator, definitions.TYPE_INDICATOR_EWF)

  @shared_test_lib.skipUnlessHasTestFile([u'image.qcow2'])
  def testScanForStorageMediaImageQCOW(self):
    """Test the ScanForStorageMediaImage() function on a QCOW image."""
    test_file = self._GetTestFilePath([u'image.qcow2'])
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForStorageMediaImage(source_path_spec)
    self.assertIsNotNone(path_spec)
    self.assertEqual(
        path_spec.type_indicator, definitions.TYPE_INDICATOR_QCOW)

  @shared_test_lib.skipUnlessHasTestFile([u'image.vhd'])
  def testScanForStorageMediaImageVHDI(self):
    """Test the ScanForStorageMediaImage() function on a VHD image."""
    test_file = self._GetTestFilePath([u'image.vhd'])
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForStorageMediaImage(source_path_spec)
    self.assertIsNotNone(path_spec)
    self.assertEqual(
        path_spec.type_indicator, definitions.TYPE_INDICATOR_VHDI)

  @shared_test_lib.skipUnlessHasTestFile([u'image.vmdk'])
  def testScanForStorageMediaImageVMDK(self):
    """Test the ScanForStorageMediaImage() function on a VMDK image."""
    test_file = self._GetTestFilePath([u'image.vmdk'])
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForStorageMediaImage(source_path_spec)
    self.assertIsNotNone(path_spec)
    self.assertEqual(
        path_spec.type_indicator, definitions.TYPE_INDICATOR_VMDK)

  @shared_test_lib.skipUnlessHasTestFile([u'mactime.body'])
  def testScanForStorageMediaImageBodyFile(self):
    """Test the ScanForStorageMediaImage() function on a body file."""
    test_file = self._GetTestFilePath([u'mactime.body'])
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForStorageMediaImage(source_path_spec)
    self.assertIsNone(path_spec)

  @shared_test_lib.skipUnlessHasTestFile([u'tsk_volume_system.raw'])
  def testScanForVolumeSystemPartitionedImage(self):
    """Test the ScanForVolumeSystem() function on a partitioned image."""
    test_file = self._GetTestFilePath([u'tsk_volume_system.raw'])
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForVolumeSystem(source_path_spec)
    self.assertIsNotNone(path_spec)
    self.assertEqual(
        path_spec.type_indicator, definitions.TYPE_INDICATOR_TSK_PARTITION)

  @shared_test_lib.skipUnlessHasTestFile([u'vsstest.qcow2'])
  def testScanForVolumeSystemVSS(self):
    """Test the ScanForVolumeSystem() function on VSS."""
    test_file = self._GetTestFilePath([u'vsstest.qcow2'])
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)
    source_path_spec = qcow_path_spec.QCOWPathSpec(parent=source_path_spec)

    path_spec = self._source_scanner.ScanForVolumeSystem(source_path_spec)
    self.assertIsNotNone(path_spec)
    self.assertEqual(
        path_spec.type_indicator, definitions.TYPE_INDICATOR_VSHADOW)

  @shared_test_lib.skipUnlessHasTestFile([u'bdetogo.raw'])
  def testScanForVolumeSystem(self):
    """Test the ScanForVolumeSystem() function on BDE."""
    test_file = self._GetTestFilePath([u'bdetogo.raw'])
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForVolumeSystem(source_path_spec)
    self.assertIsNotNone(path_spec)
    self.assertEqual(path_spec.type_indicator, definitions.TYPE_INDICATOR_BDE)

  @shared_test_lib.skipUnlessHasTestFile([u'mactime.body'])
  def testScanForVolumeSystemBodyFile(self):
    """Test the ScanForVolumeSystem() function on a body file."""
    test_file = self._GetTestFilePath([u'mactime.body'])
    source_path_spec = os_path_spec.OSPathSpec(location=test_file)

    path_spec = self._source_scanner.ScanForVolumeSystem(source_path_spec)
    self.assertIsNone(path_spec)


if __name__ == '__main__':
  unittest.main()
