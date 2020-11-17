#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the volume scanner objects."""

from __future__ import unicode_literals

import unittest

from dfvfs.helpers import source_scanner
from dfvfs.helpers import volume_scanner
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver
from dfvfs.volume import tsk_volume_system
from dfvfs.volume import vshadow_volume_system

from tests import test_lib as shared_test_lib


class TestVolumeScannerMediator(volume_scanner.VolumeScannerMediator):
  """Volume scanner mediator for testing."""

  _APFS_PASSWORD = 'apfs-TEST'
  _BDE_PASSWORD = 'bde-TEST'
  _FVDE_PASSWORD = 'fvde-TEST'

  def GetAPFSVolumeIdentifiers(self, volume_system, volume_identifiers):
    """Retrieves APFS volume identifiers.

    This method can be used to prompt the user to provide APFS volume
    identifiers.

    Args:
      volume_system (APFSVolumeSystem): volume system.
      volume_identifiers (list[str]): volume identifiers including prefix.

    Returns:
      list[str]: selected volume identifiers including prefix or None.
    """
    return volume_identifiers

  def GetLVMVolumeIdentifiers(self, volume_system, volume_identifiers):
    """Retrieves LVM volume identifiers.

    This method can be used to prompt the user to provide LVM volume
    identifiers.

    Args:
      volume_system (LVMVolumeSystem): volume system.
      volume_identifiers (list[str]): volume identifiers including prefix.

    Returns:
      list[str]: selected volume identifiers including prefix or None.
    """
    return volume_identifiers

  def GetPartitionIdentifiers(self, volume_system, volume_identifiers):
    """Retrieves partition identifiers.

    This method can be used to prompt the user to provide partition identifiers.

    Args:
      volume_system (TSKVolumeSystem): volume system.
      volume_identifiers (list[str]): volume identifiers including prefix.

    Returns:
      list[str]: selected volume identifiers including prefix or None.
    """
    return volume_identifiers

  def GetVSSStoreIdentifiers(self, volume_system, volume_identifiers):
    """Retrieves VSS store identifiers.

    This method can be used to prompt the user to provide VSS store identifiers.

    Args:
      volume_system (VShadowVolumeSystem): volume system.
      volume_identifiers (list[str]): volume identifiers including prefix.

    Returns:
      list[str]: selected volume identifiers including prefix or None.
    """
    return volume_identifiers

  def UnlockEncryptedVolume(
      self, source_scanner_object, scan_context, locked_scan_node, credentials):
    """Unlocks an encrypted volume.

    This method can be used to prompt the user to provide encrypted volume
    credentials.

    Args:
      source_scanner_object (SourceScanner): source scanner.
      scan_context (SourceScannerContext): source scanner context.
      locked_scan_node (SourceScanNode): locked scan node.
      credentials (Credentials): credentials supported by the locked scan node.

    Returns:
      bool: True if the volume was unlocked.
    """
    if locked_scan_node.type_indicator == (
        definitions.TYPE_INDICATOR_APFS_CONTAINER):
      password = self._APFS_PASSWORD

    elif locked_scan_node.type_indicator == definitions.TYPE_INDICATOR_BDE:
      password = self._BDE_PASSWORD

    elif locked_scan_node.type_indicator == definitions.TYPE_INDICATOR_FVDE:
      password = self._FVDE_PASSWORD

    return source_scanner_object.Unlock(
        scan_context, locked_scan_node.path_spec, 'password', password)


class VolumeScannerOptionsTest(shared_test_lib.BaseTestCase):
  """Tests for the volume scanner options."""

  def testInitialize(self):
    """Tests the __init__ function."""
    test_options = volume_scanner.VolumeScannerOptions()
    self.assertIsNotNone(test_options)


class VolumeScannerTest(shared_test_lib.BaseTestCase):
  """Tests for a volume scanner."""

  # pylint: disable=protected-access

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

  def testGetPartitionIdentifiers(self):
    """Tests the _GetPartitionIdentifiers function."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)
    test_options = volume_scanner.VolumeScannerOptions()

    # Test error conditions.
    with self.assertRaises(errors.ScannerError):
      test_scanner._GetPartitionIdentifiers(None, test_options)

    scan_node = source_scanner.SourceScanNode(None)
    with self.assertRaises(errors.ScannerError):
      test_scanner._GetPartitionIdentifiers(scan_node, test_options)

  def testGetTSKPartitionIdentifiersOnAPFS(self):
    """Tests the _GetTSKPartitionIdentifiers function on an APFS image."""
    # Test with mediator.
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)
    test_options = volume_scanner.VolumeScannerOptions()

    test_path = self._GetTestFilePath(['apfs_encrypted.dmg'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    identifiers = test_scanner._GetPartitionIdentifiers(scan_node, test_options)
    self.assertEqual(len(identifiers), 1)
    self.assertEqual(identifiers, ['p1'])

  def testGetTSKPartitionIdentifiersOnPartitionedImage(self):
    """Tests the _GetTSKPartitionIdentifiers function on a partitioned image."""
    # Test with mediator.
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)
    test_options = volume_scanner.VolumeScannerOptions()

    test_path = self._GetTestFilePath(['mbr.raw'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    identifiers = test_scanner._GetPartitionIdentifiers(scan_node, test_options)
    self.assertEqual(len(identifiers), 2)
    self.assertEqual(identifiers, ['p1', 'p2'])

    # Test without mediator.
    test_scanner = volume_scanner.VolumeScanner()
    test_options = volume_scanner.VolumeScannerOptions()

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    with self.assertRaises(errors.ScannerError):
      test_scanner._GetPartitionIdentifiers(scan_node, test_options)

  def testGetVSSStoreIdentifiers(self):
    """Tests the _GetVSSStoreIdentifiers function."""
    # Test with mediator.
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)
    test_options = volume_scanner.VolumeScannerOptions()

    test_path = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    identifiers = test_scanner._GetVSSStoreIdentifiers(
        scan_node.sub_nodes[0], test_options)
    self.assertEqual(len(identifiers), 2)
    self.assertEqual(identifiers, ['vss1', 'vss2'])

    # Test without mediator.
    test_scanner = volume_scanner.VolumeScanner()
    test_options = volume_scanner.VolumeScannerOptions()

    test_path = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    with self.assertRaises(errors.ScannerError):
      test_scanner._GetVSSStoreIdentifiers(scan_node.sub_nodes[0], test_options)

    # Test error conditions.
    with self.assertRaises(errors.ScannerError):
      test_scanner._GetVSSStoreIdentifiers(None, test_options)

    scan_node = source_scanner.SourceScanNode(None)
    with self.assertRaises(errors.ScannerError):
      test_scanner._GetVSSStoreIdentifiers(scan_node, test_options)

  def testNormalizedVolumeIdentifiersPartitionedImage(self):
    """Tests the _NormalizedVolumeIdentifiers function."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

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

    volume_identifiers = test_scanner._NormalizedVolumeIdentifiers(
        volume_system, ['p1', 'p2'], prefix='p')
    self.assertEqual(volume_identifiers, ['p1', 'p2'])

    volume_identifiers = test_scanner._NormalizedVolumeIdentifiers(
        volume_system, ['1', '2'], prefix='p')
    self.assertEqual(volume_identifiers, ['p1', 'p2'])

    volume_identifiers = test_scanner._NormalizedVolumeIdentifiers(
        volume_system, [1, 2], prefix='p')
    self.assertEqual(volume_identifiers, ['p1', 'p2'])

    # Test error conditions.
    with self.assertRaises(errors.ScannerError):
      test_scanner._NormalizedVolumeIdentifiers(
          volume_system, ['p3'], prefix='p')

  def testNormalizedVolumeIdentifiersVSS(self):
    """Tests the _NormalizedVolumeIdentifiers function on a VSS."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    test_path = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_qcow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_QCOW, parent=test_os_path_spec)
    test_vss_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, parent=test_qcow_path_spec)

    volume_system = vshadow_volume_system.VShadowVolumeSystem()
    volume_system.Open(test_vss_path_spec)

    volume_identifiers = test_scanner._NormalizedVolumeIdentifiers(
        volume_system, ['vss1', 'vss2'], prefix='vss')
    self.assertEqual(volume_identifiers, ['vss1', 'vss2'])

    volume_identifiers = test_scanner._NormalizedVolumeIdentifiers(
        volume_system, [1, 2], prefix='vss')
    self.assertEqual(volume_identifiers, ['vss1', 'vss2'])

    # Test error conditions.
    with self.assertRaises(errors.ScannerError):
      test_scanner._NormalizedVolumeIdentifiers(
          volume_system, ['vss3'], prefix='vss')

  def testScanEncryptedVolume(self):
    """Tests the _ScanEncryptedVolume function."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    scan_context = source_scanner.SourceScannerContext()

    # Test error conditions.
    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanEncryptedVolume(scan_context, None)

    scan_node = source_scanner.SourceScanNode(None)
    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanEncryptedVolume(scan_context, scan_node)

  def testScanEncryptedVolumeOnBDE(self):
    """Tests the _ScanEncryptedVolume function on a BDE image."""
    resolver.Resolver.key_chain.Empty()

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    test_path = self._GetTestFilePath(['bdetogo.raw'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    bde_scan_node = scan_node.sub_nodes[0]

    test_scanner._ScanEncryptedVolume(scan_context, bde_scan_node)

  def testScanEncryptedVolumeOnEncryptedAPFS(self):
    """Tests the _ScanEncryptedVolume function on an encrypted APFS image."""
    resolver.Resolver.key_chain.Empty()

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    test_path = self._GetTestFilePath(['apfs_encrypted.dmg'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    apfs_container_scan_node = scan_node.sub_nodes[4].sub_nodes[0]

    # Test on volume system sub node.
    test_scanner._ScanEncryptedVolume(
        scan_context, apfs_container_scan_node.sub_nodes[0])

  def testScanVolume(self):
    """Tests the _ScanVolume function."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)
    test_options = volume_scanner.VolumeScannerOptions()

    scan_context = source_scanner.SourceScannerContext()

    # Test error conditions.
    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanVolume(scan_context, None, test_options, [])

    scan_node = source_scanner.SourceScanNode(None)
    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanVolume(scan_context, scan_node, test_options, [])

  def testScanVolumeOnAPFS(self):
    """Tests the _ScanVolume function on an APFS image."""
    resolver.Resolver.key_chain.Empty()

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)
    test_options = volume_scanner.VolumeScannerOptions()

    test_path = self._GetTestFilePath(['apfs.raw'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = scan_context.GetRootScanNode()

    apfs_container_scan_node = scan_node.sub_nodes[0].sub_nodes[0]

    # Test on volume system root node.
    base_path_specs = []
    test_scanner._ScanVolume(
        scan_context, apfs_container_scan_node, test_options, base_path_specs)
    self.assertEqual(len(base_path_specs), 1)

    # Test on volume system sub node.
    base_path_specs = []
    test_scanner._ScanVolume(
        scan_context, apfs_container_scan_node.sub_nodes[0], test_options,
        base_path_specs)
    self.assertEqual(len(base_path_specs), 1)

  def testScanVolumeOnBDE(self):
    """Tests the _ScanVolume function on a BDE image."""
    resolver.Resolver.key_chain.Empty()

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)
    test_options = volume_scanner.VolumeScannerOptions()

    test_path = self._GetTestFilePath(['bdetogo.raw'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    bde_scan_node = scan_node.sub_nodes[0]

    base_path_specs = []
    test_scanner._ScanVolume(
        scan_context, bde_scan_node, test_options, base_path_specs)
    self.assertEqual(len(base_path_specs), 1)

  def testScanVolumeOnEncryptedAPFS(self):
    """Tests the _ScanVolume function on an encrypted APFS image."""
    resolver.Resolver.key_chain.Empty()

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)
    test_options = volume_scanner.VolumeScannerOptions()

    test_path = self._GetTestFilePath(['apfs_encrypted.dmg'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    apfs_container_scan_node = scan_node.sub_nodes[4].sub_nodes[0]

    # Test on volume system root node.
    base_path_specs = []
    test_scanner._ScanVolume(
        scan_context, apfs_container_scan_node, test_options, base_path_specs)
    self.assertEqual(len(base_path_specs), 1)

    # Test on volume system sub node.
    base_path_specs = []
    test_scanner._ScanVolume(
        scan_context, apfs_container_scan_node.sub_nodes[0], test_options,
        base_path_specs)
    self.assertEqual(len(base_path_specs), 1)

  def testScanVolumeOnRAW(self):
    """Tests the _ScanVolume function on a RAW image."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)
    test_options = volume_scanner.VolumeScannerOptions()

    test_path = self._GetTestFilePath(['ext2.raw'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = scan_context.GetRootScanNode()

    base_path_specs = []
    test_scanner._ScanVolume(
        scan_context, scan_node, test_options, base_path_specs)
    self.assertEqual(len(base_path_specs), 1)

  def testScanVolumeOnVSS(self):
    """Tests the _ScanVolume function on VSS."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)
    test_options = volume_scanner.VolumeScannerOptions()

    test_path = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    vss_scan_node = scan_node.sub_nodes[0]

    # Test on volume system root node.
    base_path_specs = []
    test_scanner._ScanVolume(
        scan_context, vss_scan_node, test_options, base_path_specs)
    self.assertEqual(len(base_path_specs), 2)

    # Test on volume system sub node.
    base_path_specs = []
    test_scanner._ScanVolume(
        scan_context, vss_scan_node.sub_nodes[0], test_options, base_path_specs)
    self.assertEqual(len(base_path_specs), 1)

  def testScanVolumeSystemRoot(self):
    """Tests the _ScanVolumeSystemRoot function."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)
    test_options = volume_scanner.VolumeScannerOptions()

    scan_context = source_scanner.SourceScannerContext()

    # Test error conditions.
    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanVolumeSystemRoot(scan_context, None, test_options, [])

    scan_node = source_scanner.SourceScanNode(None)
    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanVolumeSystemRoot(
          scan_context, scan_node, test_options, [])

  def testScanVolumeSystemRootOnAPFS(self):
    """Tests the _ScanVolumeSystemRoot function on an APFS image."""
    resolver.Resolver.key_chain.Empty()

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)
    test_options = volume_scanner.VolumeScannerOptions()

    test_path = self._GetTestFilePath(['apfs_encrypted.dmg'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    apfs_container_scan_node = scan_node.sub_nodes[4].sub_nodes[0]

    base_path_specs = []
    test_scanner._ScanVolumeSystemRoot(
        scan_context, apfs_container_scan_node, test_options,
        base_path_specs)
    self.assertEqual(len(base_path_specs), 1)

    # Test error conditions.
    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanVolumeSystemRoot(
          scan_context, apfs_container_scan_node.sub_nodes[0], test_options,
          base_path_specs)

  def testScanVolumeSystemRootOnPartitionedImage(self):
    """Tests the _ScanVolumeSystemRoot function on a partitioned image."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)
    test_options = volume_scanner.VolumeScannerOptions()

    test_path = self._GetTestFilePath(['mbr.raw'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    # Test error conditions.
    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanVolumeSystemRoot(
          scan_context, scan_node, test_options, [])

  def testScanVolumeSystemRootOnVSS(self):
    """Tests the _ScanVolumeSystemRoot function on VSS."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)
    test_options = volume_scanner.VolumeScannerOptions()

    test_path = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    vss_scan_node = scan_node.sub_nodes[0]

    base_path_specs = []
    test_scanner._ScanVolumeSystemRoot(
        scan_context, vss_scan_node, test_options, base_path_specs)
    self.assertEqual(len(base_path_specs), 2)

  def testGetBasePathSpecsOnRAW(self):
    """Tests the GetBasePathSpecs function on a RAW image."""
    test_path = self._GetTestFilePath(['ext2.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    test_tsk_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/', parent=test_raw_path_spec)

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    expected_base_path_specs = [test_tsk_path_spec.comparable]

    base_path_specs = test_scanner.GetBasePathSpecs(test_path)
    base_path_specs = [
        base_path_spec.comparable for base_path_spec in base_path_specs]

    self.assertEqual(base_path_specs, expected_base_path_specs)

    # Test error conditions.
    with self.assertRaises(errors.ScannerError):
      test_scanner.GetBasePathSpecs(None)

    with self.assertRaises(errors.ScannerError):
      test_scanner.GetBasePathSpecs('/bogus')

  def testGetBasePathSpecsOnPartitionedImage(self):
    """Tests the GetBasePathSpecs function on a partitioned image."""
    test_path = self._GetTestFilePath(['mbr.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)

    test_tsk_partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/p1', part_index=2,
        start_offset=0x00000200, parent=test_raw_path_spec)
    test_tsk_path_spec1 = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/',
        parent=test_tsk_partition_path_spec)

    test_tsk_partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/p2', part_index=6,
        start_offset=0x00010600, parent=test_raw_path_spec)
    test_tsk_path_spec2 = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/',
        parent=test_tsk_partition_path_spec)

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    expected_base_path_specs = [
        test_tsk_path_spec1.comparable, test_tsk_path_spec2.comparable]

    base_path_specs = test_scanner.GetBasePathSpecs(test_path)
    base_path_specs = [
        base_path_spec.comparable for base_path_spec in base_path_specs]

    self.assertEqual(base_path_specs, expected_base_path_specs)

  def testGetBasePathSpecsOnDirectory(self):
    """Tests the GetBasePathSpecs function on a directory."""
    test_path = self._GetTestFilePath(['testdir_os'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    expected_base_path_specs = [test_os_path_spec.comparable]

    base_path_specs = test_scanner.GetBasePathSpecs(test_path)
    base_path_specs = [
        base_path_spec.comparable for base_path_spec in base_path_specs]

    self.assertEqual(base_path_specs, expected_base_path_specs)


class WindowsVolumeScannerTest(shared_test_lib.BaseTestCase):
  """Tests for a Windows volume scanner."""

  # pylint: disable=protected-access

  def testScanFileSystem(self):
    """Tests the _ScanFileSystem function."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.WindowsVolumeScanner(mediator=test_mediator)

    test_path = self._GetTestFilePath(['windows_volume.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_qcow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_QCOW, parent=test_os_path_spec)
    test_tsk_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/',
        parent=test_qcow_path_spec)

    scan_node = source_scanner.SourceScanNode(test_tsk_path_spec)

    base_path_specs = []
    test_scanner._ScanFileSystem(scan_node, base_path_specs)
    self.assertEqual(len(base_path_specs), 1)

    # Test error conditions.
    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanFileSystem(None, [])

    scan_node = source_scanner.SourceScanNode(None)
    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanFileSystem(scan_node, [])

  # _ScanFileSystemForWindowsDirectory is tested by testScanFileSystem.

  def testOpenFile(self):
    """Tests the OpenFile function."""
    test_path = self._GetTestFilePath(['windows_volume.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.WindowsVolumeScanner(mediator=test_mediator)

    result = test_scanner.ScanForWindowsVolume(test_path)
    self.assertTrue(result)

    file_object = test_scanner.OpenFile(
        'C:\\Windows\\System32\\config\\syslog')
    self.assertIsNotNone(file_object)
    file_object.close()

    file_object = test_scanner.OpenFile('C:\\bogus')
    self.assertIsNone(file_object)

    location = 'C:\\Windows\\System32\\config'
    if definitions.PREFERRED_NTFS_BACK_END == definitions.TYPE_INDICATOR_NTFS:
      file_object = test_scanner.OpenFile(location)
      self.assertIsNone(file_object)
    else:
      with self.assertRaises(IOError):
        test_scanner.OpenFile(location)

  def testScanForWindowsVolume(self):
    """Tests the ScanForWindowsVolume function."""
    test_path = self._GetTestFilePath(['mbr.raw'])
    self._SkipIfPathNotExists(test_path)

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.WindowsVolumeScanner(mediator=test_mediator)

    result = test_scanner.ScanForWindowsVolume(test_path)
    self.assertFalse(result)

    test_path = self._GetTestFilePath(['windows_volume.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.WindowsVolumeScanner(mediator=test_mediator)

    result = test_scanner.ScanForWindowsVolume(test_path)
    self.assertTrue(result)


if __name__ == '__main__':
  unittest.main()
