#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the source scanner object."""

from __future__ import unicode_literals

import unittest

from dfvfs.helpers import source_scanner
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.path import fake_path_spec
from dfvfs.resolver import resolver
from dfvfs.volume import tsk_volume_system

from tests import test_lib as shared_test_lib


class SourceScanNodeTest(shared_test_lib.BaseTestCase):
  """Tests the source scanner node."""

  def testTypeIndicator(self):
    """Test the type_indicator property."""
    test_fake_path_spec = fake_path_spec.FakePathSpec(location='/')
    test_node = source_scanner.SourceScanNode(test_fake_path_spec)

    self.assertEqual(test_node.type_indicator, definitions.TYPE_INDICATOR_FAKE)

  def testGetSubNodeByLocation(self):
    """Test the GetSubNodeByLocation function."""
    test_fake_path_spec = fake_path_spec.FakePathSpec(location='/')
    test_node = source_scanner.SourceScanNode(test_fake_path_spec)

    sub_node = test_node.GetSubNodeByLocation('/')
    self.assertIsNone(sub_node)

  def testGetUnscannedSubNode(self):
    """Test the GetUnscannedSubNode function."""
    test_fake_path_spec = fake_path_spec.FakePathSpec(location='/')
    test_node = source_scanner.SourceScanNode(test_fake_path_spec)

    sub_node = test_node.GetUnscannedSubNode()
    self.assertIsNotNone(sub_node)

  def testIsSystemLevel(self):
    """Test the IsSystemLevel function."""
    test_fake_path_spec = fake_path_spec.FakePathSpec(location='/')
    test_node = source_scanner.SourceScanNode(test_fake_path_spec)

    self.assertTrue(test_node.IsSystemLevel())

  def testSupportsEncryption(self):
    """Test the SupportsEncryption function."""
    test_fake_path_spec = fake_path_spec.FakePathSpec(location='/')
    test_node = source_scanner.SourceScanNode(test_fake_path_spec)

    self.assertFalse(test_node.SupportsEncryption())


class SourceScannerContextTest(shared_test_lib.BaseTestCase):
  """Tests the source scanner context."""

  # pylint: disable=protected-access

  def testLockedScanNodes(self):
    """Test the locked_scan_nodes property."""
    test_context = source_scanner.SourceScannerContext()

    locked_scan_nodes = list(test_context.locked_scan_nodes)
    self.assertEqual(locked_scan_nodes, [])

  def testAddScanNode(self):
    """Test the AddScanNode function."""
    test_context = source_scanner.SourceScannerContext()

    self.assertEqual(len(test_context._scan_nodes), 0)

    test_fake_path_spec = fake_path_spec.FakePathSpec(location='/')
    test_context.AddScanNode(test_fake_path_spec, None)

    self.assertEqual(len(test_context._scan_nodes), 1)

  def testGetRootScanNode(self):
    """Test the GetRootScanNode function."""
    test_fake_path_spec = fake_path_spec.FakePathSpec(location='/')
    test_context = source_scanner.SourceScannerContext()

    root_node = test_context.GetRootScanNode()
    self.assertIsNone(root_node)

    test_context.AddScanNode(test_fake_path_spec, None)

    root_node = test_context.GetRootScanNode()
    self.assertIsNotNone(root_node)

  def testGetScanNode(self):
    """Test the GetScanNode function."""
    test_fake_path_spec = fake_path_spec.FakePathSpec(location='/')
    test_context = source_scanner.SourceScannerContext()

    scan_node = test_context.GetScanNode(test_fake_path_spec)
    self.assertIsNone(scan_node)

    test_context.AddScanNode(test_fake_path_spec, None)

    scan_node = test_context.GetScanNode(test_fake_path_spec)
    self.assertIsNotNone(scan_node)

  def testGetUnscannedScanNode(self):
    """Test the GetUnscannedScanNode function."""
    test_fake_path_spec = fake_path_spec.FakePathSpec(location='/')
    test_context = source_scanner.SourceScannerContext()

    scan_node = test_context.GetUnscannedScanNode()
    self.assertIsNone(scan_node)

    test_context.AddScanNode(test_fake_path_spec, None)

    scan_node = test_context.GetUnscannedScanNode()
    self.assertIsNotNone(scan_node)

  def testHasFileSystemScanNodes(self):
    """Test the HasFileSystemScanNodes function."""
    test_fake_path_spec = fake_path_spec.FakePathSpec(location='/')
    test_context = source_scanner.SourceScannerContext()

    self.assertFalse(test_context.HasFileSystemScanNodes())

    test_context.AddScanNode(test_fake_path_spec, None)

    self.assertTrue(test_context.HasFileSystemScanNodes())

  def testHasLockedScanNodes(self):
    """Test the HasLockedScanNodes function."""
    test_fake_path_spec = fake_path_spec.FakePathSpec(location='/')
    test_context = source_scanner.SourceScannerContext()

    self.assertFalse(test_context.HasLockedScanNodes())

    test_context.AddScanNode(test_fake_path_spec, None)

    self.assertFalse(test_context.HasLockedScanNodes())

    test_context.LockScanNode(test_fake_path_spec)

    self.assertTrue(test_context.HasLockedScanNodes())

  def testHasScanNode(self):
    """Test the HasScanNode function."""
    test_fake_path_spec = fake_path_spec.FakePathSpec(location='/')
    test_context = source_scanner.SourceScannerContext()

    self.assertFalse(test_context.HasScanNode(test_fake_path_spec))

    test_context.AddScanNode(test_fake_path_spec, None)

    self.assertTrue(test_context.HasScanNode(test_fake_path_spec))

  def testIsLockedScanNode(self):
    """Test the IsLockedScanNode function."""
    test_fake_path_spec = fake_path_spec.FakePathSpec(location='/')
    test_context = source_scanner.SourceScannerContext()

    self.assertFalse(test_context.IsLockedScanNode(test_fake_path_spec))

    test_context.AddScanNode(test_fake_path_spec, None)

    self.assertFalse(test_context.IsLockedScanNode(test_fake_path_spec))

    test_context.LockScanNode(test_fake_path_spec)

    self.assertTrue(test_context.IsLockedScanNode(test_fake_path_spec))

  def testIsSourceTypeDirectory(self):
    """Test the IsSourceTypeDirectory function."""
    test_context = source_scanner.SourceScannerContext()

    self.assertIsNone(test_context.IsSourceTypeDirectory())

    test_context.source_type = definitions.SOURCE_TYPE_DIRECTORY
    self.assertTrue(test_context.IsSourceTypeDirectory())

    test_context.source_type = definitions.SOURCE_TYPE_FILE
    self.assertFalse(test_context.IsSourceTypeDirectory())

  def testIsSourceTypeFile(self):
    """Test the IsSourceTypeFile function."""
    test_context = source_scanner.SourceScannerContext()

    self.assertIsNone(test_context.IsSourceTypeFile())

    test_context.source_type = definitions.SOURCE_TYPE_FILE
    self.assertTrue(test_context.IsSourceTypeFile())

    test_context.source_type = definitions.SOURCE_TYPE_DIRECTORY
    self.assertFalse(test_context.IsSourceTypeFile())

  def testLockScanNode(self):
    """Test the LockScanNode function."""
    test_fake_path_spec = fake_path_spec.FakePathSpec(location='/')
    test_context = source_scanner.SourceScannerContext()

    with self.assertRaises(KeyError):
      test_context.LockScanNode(test_fake_path_spec)

    test_context.AddScanNode(test_fake_path_spec, None)

    test_context.LockScanNode(test_fake_path_spec)

  def testOpenSourcePath(self):
    """Test the OpenSourcePath function."""
    test_context = source_scanner.SourceScannerContext()

    self.assertEqual(len(test_context._scan_nodes), 0)

    test_path = self._GetTestFilePath(['testdir_os', 'file1.txt'])
    test_context.OpenSourcePath(test_path)

    self.assertEqual(len(test_context._scan_nodes), 1)

  def testRemoveScanNode(self):
    """Test the RemoveScanNode function."""
    test_fake_path_spec = fake_path_spec.FakePathSpec(location='/')
    test_context = source_scanner.SourceScannerContext()

    parent_node = test_context.RemoveScanNode(test_fake_path_spec)
    self.assertIsNone(parent_node)

    self.assertEqual(len(test_context._scan_nodes), 0)

    test_context.AddScanNode(test_fake_path_spec, None)

    self.assertEqual(len(test_context._scan_nodes), 1)

    parent_node = test_context.RemoveScanNode(test_fake_path_spec)
    self.assertIsNone(parent_node)

    self.assertEqual(len(test_context._scan_nodes), 0)

  def testSetSourceType(self):
    """Test the SetSourceType function."""
    test_context = source_scanner.SourceScannerContext()

    test_context.SetSourceType(definitions.SOURCE_TYPE_FILE)
    self.assertEqual(test_context.source_type, definitions.SOURCE_TYPE_FILE)

    test_context.SetSourceType(definitions.SOURCE_TYPE_DIRECTORY)
    self.assertEqual(test_context.source_type, definitions.SOURCE_TYPE_FILE)

  def testUnlockScanNode(self):
    """Test the UnlockScanNode function."""
    test_fake_path_spec = fake_path_spec.FakePathSpec(location='/')
    test_context = source_scanner.SourceScannerContext()

    with self.assertRaises(KeyError):
      test_context.UnlockScanNode(test_fake_path_spec)

    test_context.AddScanNode(test_fake_path_spec, None)

    with self.assertRaises(KeyError):
      test_context.UnlockScanNode(test_fake_path_spec)

    test_context.LockScanNode(test_fake_path_spec)

    test_context.UnlockScanNode(test_fake_path_spec)


class SourceScannerTest(shared_test_lib.BaseTestCase):
  """The unit test for the source scanner."""

  _APFS_PASSWORD = 'apfs-TEST'
  _BDE_PASSWORD = 'bde-TEST'
  _FVDE_PASSWORD = 'fvde-TEST'

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

  # TODO: add tests for _ScanEncryptedVolumeNode.
  # TODO: add tests for _ScanNode.
  # TODO: add tests for _ScanVolumeSystemRootNode.

  def testGetVolumeIdentifiers(self):
    """Test the GetVolumeIdentifiers function."""
    test_path = self._GetTestFilePath(['mbr.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    test_tsk_partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, parent=test_raw_path_spec)

    volume_system = tsk_volume_system.TSKVolumeSystem()
    volume_system.Open(test_tsk_partition_path_spec)

    volume_identifiers = self._source_scanner.GetVolumeIdentifiers(
        volume_system)
    self.assertEqual(volume_identifiers, ['p1', 'p2'])

  def testScanOnAPFS(self):
    """Test the Scan function on an APFS image."""
    test_path = self._GetTestFilePath(['apfs.raw'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    self._source_scanner.Scan(scan_context)
    self.assertEqual(
        scan_context.source_type, definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)

    scan_node = scan_context.GetRootScanNode()
    self.assertIsNotNone(scan_node)

    scan_node = scan_node.sub_nodes[0].sub_nodes[0]
    self.assertIsNotNone(scan_node)
    self.assertEqual(
        scan_node.type_indicator, definitions.TYPE_INDICATOR_APFS_CONTAINER)
    self.assertEqual(len(scan_node.sub_nodes), 1)

    scan_node = scan_node.sub_nodes[0]
    self.assertIsNotNone(scan_node)
    self.assertEqual(
        scan_node.type_indicator, definitions.TYPE_INDICATOR_APFS_CONTAINER)
    self.assertEqual(len(scan_node.sub_nodes), 1)

    scan_node = scan_node.GetSubNodeByLocation('/')
    self.assertIsNotNone(scan_node)
    self.assertEqual(scan_node.type_indicator, definitions.TYPE_INDICATOR_APFS)

  def testScanOnEncryptedAPFS(self):
    """Test the Scan function on an encrypted APFS image."""
    resolver.Resolver.key_chain.Empty()

    test_path = self._GetTestFilePath(['apfs_encrypted.dmg'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    self._source_scanner.Scan(scan_context)
    self.assertEqual(
        scan_context.source_type, definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)

    scan_node = self._GetTestScanNode(scan_context)
    self.assertIsNotNone(scan_node)
    self.assertEqual(
        scan_node.type_indicator, definitions.TYPE_INDICATOR_TSK_PARTITION)

    self.assertEqual(len(scan_node.sub_nodes), 6)

    scan_node = scan_node.sub_nodes[4].GetSubNodeByLocation('/')
    self.assertIsNotNone(scan_node)
    self.assertEqual(
        scan_node.type_indicator, definitions.TYPE_INDICATOR_APFS_CONTAINER)

    self.assertEqual(len(scan_node.sub_nodes), 1)

    scan_node = scan_node.sub_nodes[0]
    self.assertIsNotNone(scan_node)
    self.assertEqual(
        scan_node.type_indicator, definitions.TYPE_INDICATOR_APFS_CONTAINER)
    self.assertEqual(len(scan_node.sub_nodes), 0)

    self.assertTrue(scan_context.IsLockedScanNode(scan_node.path_spec))

    self._source_scanner.Unlock(
        scan_context, scan_node.path_spec, 'password', self._APFS_PASSWORD)

    self.assertFalse(scan_context.IsLockedScanNode(scan_node.path_spec))

    self._source_scanner.Scan(scan_context, scan_path_spec=scan_node.path_spec)
    self.assertEqual(len(scan_node.sub_nodes), 1)

    scan_node = scan_node.GetSubNodeByLocation('/')
    self.assertIsNotNone(scan_node)
    self.assertEqual(scan_node.type_indicator, definitions.TYPE_INDICATOR_APFS)

  def testScanOnLVM(self):
    """Test the Scan function on LVM."""
    test_path = self._GetTestFilePath(['lvm.raw'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    self._source_scanner.Scan(scan_context)
    self.assertEqual(
        scan_context.source_type, definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)

    scan_node = self._GetTestScanNode(scan_context)
    self.assertIsNotNone(scan_node)
    self.assertEqual(scan_node.type_indicator, definitions.TYPE_INDICATOR_LVM)

    self.assertEqual(len(scan_node.sub_nodes), 2)

    scan_node = scan_node.sub_nodes[0].GetSubNodeByLocation('/')
    self.assertIsNotNone(scan_node)
    self.assertEqual(scan_node.type_indicator, definitions.TYPE_INDICATOR_TSK)

  def testScanOnMBRPartitionedImage(self):
    """Test the Scan function on a MBR partitioned image."""
    test_path = self._GetTestFilePath(['mbr.raw'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    self._source_scanner.Scan(scan_context)
    self.assertEqual(
        scan_context.source_type, definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)

    scan_node = self._GetTestScanNode(scan_context)
    self.assertIsNotNone(scan_node)
    self.assertEqual(
        scan_node.type_indicator, definitions.TYPE_INDICATOR_TSK_PARTITION)

    self.assertEqual(len(scan_node.sub_nodes), 8)

    scan_node = scan_node.sub_nodes[6].GetSubNodeByLocation('/')
    self.assertIsNotNone(scan_node)
    self.assertEqual(scan_node.type_indicator, definitions.TYPE_INDICATOR_TSK)

  def testScanOnVSS(self):
    """Test the Scan function on VSS."""
    test_path = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

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

    if definitions.PREFERRED_NTFS_BACK_END == definitions.TYPE_INDICATOR_NTFS:
      sub_node_location = '\\'
    else:
      sub_node_location = '/'

    scan_node = scan_node.GetSubNodeByLocation(sub_node_location)
    self.assertIsNotNone(scan_node)

    expected_type_indicator = definitions.PREFERRED_NTFS_BACK_END
    self.assertEqual(scan_node.type_indicator, expected_type_indicator)

  def testScanOnBDE(self):
    """Test the Scan function on BDE."""
    resolver.Resolver.key_chain.Empty()

    test_path = self._GetTestFilePath(['bdetogo.raw'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    self._source_scanner.Scan(scan_context)
    self.assertEqual(
        scan_context.source_type, definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)

    scan_node = self._GetTestScanNode(scan_context)
    self.assertIsNotNone(scan_node)
    self.assertEqual(scan_node.type_indicator, definitions.TYPE_INDICATOR_RAW)

    scan_node = scan_node.GetSubNodeByLocation(None)
    self.assertIsNotNone(scan_node)
    self.assertEqual(scan_node.type_indicator, definitions.TYPE_INDICATOR_BDE)
    self.assertEqual(len(scan_node.sub_nodes), 0)

    self.assertTrue(scan_context.IsLockedScanNode(scan_node.path_spec))

    self._source_scanner.Unlock(
        scan_context, scan_node.path_spec, 'password', self._BDE_PASSWORD)

    self.assertFalse(scan_context.IsLockedScanNode(scan_node.path_spec))

    self._source_scanner.Scan(scan_context, scan_path_spec=scan_node.path_spec)
    self.assertEqual(len(scan_node.sub_nodes), 1)

    scan_node = scan_node.GetSubNodeByLocation('/')
    self.assertIsNotNone(scan_node)
    self.assertIsNotNone(scan_node.path_spec)
    self.assertEqual(scan_node.type_indicator, definitions.TYPE_INDICATOR_TSK)

  def testScanOnFVDE(self):
    """Test the Scan function on FVDE."""
    resolver.Resolver.key_chain.Empty()

    test_path = self._GetTestFilePath(['fvdetest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    self._source_scanner.Scan(scan_context)
    self.assertEqual(
        scan_context.source_type, definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)

    scan_node = self._GetTestScanNode(scan_context)
    self.assertIsNotNone(scan_node)
    self.assertEqual(
        scan_node.type_indicator, definitions.TYPE_INDICATOR_TSK_PARTITION)

    scan_node = scan_node.GetSubNodeByLocation('/p1')
    scan_node = scan_node.sub_nodes[0]

    self.assertIsNotNone(scan_node)
    self.assertEqual(scan_node.type_indicator, definitions.TYPE_INDICATOR_FVDE)
    self.assertEqual(len(scan_node.sub_nodes), 0)

    self.assertTrue(scan_context.IsLockedScanNode(scan_node.path_spec))

    self._source_scanner.Unlock(
        scan_context, scan_node.path_spec, 'password', self._FVDE_PASSWORD)

    self.assertFalse(scan_context.IsLockedScanNode(scan_node.path_spec))

    self._source_scanner.Scan(scan_context, scan_path_spec=scan_node.path_spec)
    self.assertEqual(len(scan_node.sub_nodes), 1)

    scan_node = scan_node.GetSubNodeByLocation('/')
    self.assertIsNotNone(scan_node)
    self.assertIsNotNone(scan_node.path_spec)
    self.assertEqual(scan_node.type_indicator, definitions.TYPE_INDICATOR_TSK)

  def testScanOnDirectory(self):
    """Test the Scan function on a directory."""
    test_path = self._GetTestFilePath(['testdir_os'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    self._source_scanner.Scan(scan_context)
    self.assertEqual(
        scan_context.source_type, definitions.SOURCE_TYPE_DIRECTORY)

    scan_node = self._GetTestScanNode(scan_context)
    self.assertIsNotNone(scan_node)
    self.assertIsNotNone(scan_node.path_spec)
    self.assertEqual(scan_node.type_indicator, definitions.TYPE_INDICATOR_OS)

  def testScanOnFile(self):
    """Test the Scan function on a file."""
    test_path = self._GetTestFilePath(['testdir_os', 'file1.txt'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    self._source_scanner.Scan(scan_context)
    self.assertEqual(scan_context.source_type, definitions.SOURCE_TYPE_FILE)

    scan_node = self._GetTestScanNode(scan_context)
    self.assertIsNotNone(scan_node)
    self.assertIsNotNone(scan_node.path_spec)
    self.assertEqual(scan_node.type_indicator, definitions.TYPE_INDICATOR_OS)

  def testScanOnRAW(self):
    """Test the Scan function on a RAW image."""
    test_path = self._GetTestFilePath(['ext2.raw'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    self._source_scanner.Scan(scan_context)
    self.assertEqual(
        scan_context.source_type, definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)

    scan_node = self._GetTestScanNode(scan_context)
    self.assertIsNotNone(scan_node)
    self.assertIsNotNone(scan_node.path_spec)
    self.assertEqual(scan_node.type_indicator, definitions.TYPE_INDICATOR_TSK)

    self.assertEqual(len(scan_node.sub_nodes), 0)

  def testScanOnNonExisting(self):
    """Test the Scan function on non-existing image file."""
    test_path = self._GetTestFilePath(['nosuchfile.raw'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    with self.assertRaises(errors.BackEndError):
      self._source_scanner.Scan(scan_context)

  def testScanForFileSystemOnVSS(self):
    """Test the ScanForFileSystem function on VSS."""
    test_path = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_qcow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_QCOW, parent=test_os_path_spec)
    test_vss_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, store_index=1,
        parent=test_qcow_path_spec)

    path_spec = self._source_scanner.ScanForFileSystem(test_vss_path_spec)
    self.assertIsNotNone(path_spec)

    expected_type_indicator = definitions.PREFERRED_NTFS_BACK_END
    self.assertEqual(path_spec.type_indicator, expected_type_indicator)

  def testScanForFileSystemOnBodyFile(self):
    """Test the ScanForFileSystem function on a body file."""
    test_path = self._GetTestFilePath(['mactime.body'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    path_spec = self._source_scanner.ScanForFileSystem(test_os_path_spec)
    self.assertIsNone(path_spec)

  def testScanForStorageMediaImageOnRAW(self):
    """Test the ScanForStorageMediaImage function on a RAW image."""
    test_path = self._GetTestFilePath(['ext2.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    path_spec = self._source_scanner.ScanForStorageMediaImage(test_os_path_spec)
    self.assertIsNotNone(path_spec)
    self.assertEqual(path_spec.type_indicator, definitions.TYPE_INDICATOR_RAW)

  def testScanForStorageMediaImageOnSplitRAW(self):
    """Test the ScanForStorageMediaImage function on a split RAW image."""
    test_path = self._GetTestFilePath(['ext2.splitraw.000'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    path_spec = self._source_scanner.ScanForStorageMediaImage(test_os_path_spec)
    self.assertIsNotNone(path_spec)
    self.assertEqual(path_spec.type_indicator, definitions.TYPE_INDICATOR_RAW)

  def testScanForStorageMediaImageOnEWF(self):
    """Test the ScanForStorageMediaImage function on an EWF image."""
    test_path = self._GetTestFilePath(['ext2.E01'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    path_spec = self._source_scanner.ScanForStorageMediaImage(test_os_path_spec)
    self.assertIsNotNone(path_spec)
    self.assertEqual(path_spec.type_indicator, definitions.TYPE_INDICATOR_EWF)

  def testScanForStorageMediaImageOnQCOW(self):
    """Test the ScanForStorageMediaImage function on a QCOW image."""
    test_path = self._GetTestFilePath(['ext2.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    path_spec = self._source_scanner.ScanForStorageMediaImage(test_os_path_spec)
    self.assertIsNotNone(path_spec)
    self.assertEqual(
        path_spec.type_indicator, definitions.TYPE_INDICATOR_QCOW)

  def testScanForStorageMediaImageOnVHDI(self):
    """Test the ScanForStorageMediaImage function on a VHD image."""
    test_path = self._GetTestFilePath(['ext2.vhd'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    path_spec = self._source_scanner.ScanForStorageMediaImage(test_os_path_spec)
    self.assertIsNotNone(path_spec)
    self.assertEqual(
        path_spec.type_indicator, definitions.TYPE_INDICATOR_VHDI)

    test_path = self._GetTestFilePath(['ext2.vhdx'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    path_spec = self._source_scanner.ScanForStorageMediaImage(test_os_path_spec)
    self.assertIsNotNone(path_spec)
    self.assertEqual(
        path_spec.type_indicator, definitions.TYPE_INDICATOR_VHDI)

  def testScanForStorageMediaImageOnVMDK(self):
    """Test the ScanForStorageMediaImage function on a VMDK image."""
    test_path = self._GetTestFilePath(['ext2.vmdk'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    path_spec = self._source_scanner.ScanForStorageMediaImage(test_os_path_spec)
    self.assertIsNotNone(path_spec)
    self.assertEqual(
        path_spec.type_indicator, definitions.TYPE_INDICATOR_VMDK)

  def testScanForStorageMediaImageOnBodyFile(self):
    """Test the ScanForStorageMediaImage function on a body file."""
    test_path = self._GetTestFilePath(['mactime.body'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    path_spec = self._source_scanner.ScanForStorageMediaImage(test_os_path_spec)
    self.assertIsNone(path_spec)

  def testScanForVolumeSystemOnPartitionedImage(self):
    """Test the ScanForVolumeSystem function on a partitioned image."""
    test_path = self._GetTestFilePath(['mbr.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    path_spec = self._source_scanner.ScanForVolumeSystem(test_os_path_spec)
    self.assertIsNotNone(path_spec)
    self.assertEqual(
        path_spec.type_indicator, definitions.TYPE_INDICATOR_TSK_PARTITION)

  def testScanForVolumeSystemOnVSS(self):
    """Test the ScanForVolumeSystem function on VSS."""
    test_path = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_qcow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_QCOW, parent=test_os_path_spec)

    path_spec = self._source_scanner.ScanForVolumeSystem(test_qcow_path_spec)
    self.assertIsNotNone(path_spec)
    self.assertEqual(
        path_spec.type_indicator, definitions.TYPE_INDICATOR_VSHADOW)

  def testScanForVolumeSystemOnBDE(self):
    """Test the ScanForVolumeSystem function on BDE."""
    resolver.Resolver.key_chain.Empty()

    test_path = self._GetTestFilePath(['bdetogo.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    path_spec = self._source_scanner.ScanForVolumeSystem(test_os_path_spec)
    self.assertIsNotNone(path_spec)
    self.assertEqual(path_spec.type_indicator, definitions.TYPE_INDICATOR_BDE)

  def testScanForVolumeSystemOnBodyFile(self):
    """Test the ScanForVolumeSystem function on a body file."""
    test_path = self._GetTestFilePath(['mactime.body'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    path_spec = self._source_scanner.ScanForVolumeSystem(test_os_path_spec)
    self.assertIsNone(path_spec)


if __name__ == '__main__':
  unittest.main()
