#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the volume scanner objects."""

from __future__ import unicode_literals

import unittest

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import fake_path_spec
from dfvfs.path import factory as path_spec_factory
from dfvfs.helpers import source_scanner
from dfvfs.helpers import volume_scanner
from dfvfs.resolver import resolver
from dfvfs.volume import tsk_volume_system
from dfvfs.volume import vshadow_volume_system

from tests import test_lib as shared_test_lib


class TestVolumeScannerMediator(volume_scanner.VolumeScannerMediator):
  """Class that defines a volume scanner mediator for testing."""

  _BDE_PASSWORD = 'bde-TEST'

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
    return source_scanner_object.Unlock(
        scan_context, locked_scan_node.path_spec, 'password',
        self._BDE_PASSWORD)


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

  def testGetTSKPartitionIdentifiers(self):
    """Tests the _GetTSKPartitionIdentifiers function."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    # Test error conditions.
    with self.assertRaises(errors.ScannerError):
      test_scanner._GetTSKPartitionIdentifiers(None)

    scan_node = source_scanner.SourceScanNode(None)
    with self.assertRaises(errors.ScannerError):
      test_scanner._GetTSKPartitionIdentifiers(scan_node)

  @shared_test_lib.skipUnlessHasTestFile(['apfs.dmg'])
  def testGetTSKPartitionIdentifiersOnAPFS(self):
    """Tests the _GetTSKPartitionIdentifiers function on an APFS image."""
    # Test with mediator.
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    test_path = self._GetTestFilePath(['apfs.dmg'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    identifiers = test_scanner._GetTSKPartitionIdentifiers(scan_node)
    self.assertEqual(len(identifiers), 1)
    self.assertEqual(identifiers, ['p1'])

  @shared_test_lib.skipUnlessHasTestFile(['tsk_volume_system.raw'])
  def testGetTSKPartitionIdentifiersOnPartitionedImage(self):
    """Tests the _GetTSKPartitionIdentifiers function on a partitioned image."""
    # Test with mediator.
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    test_path = self._GetTestFilePath(['tsk_volume_system.raw'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    identifiers = test_scanner._GetTSKPartitionIdentifiers(scan_node)
    self.assertEqual(len(identifiers), 2)
    self.assertEqual(identifiers, ['p1', 'p2'])

    # Test without mediator.
    test_scanner = volume_scanner.VolumeScanner()

    test_path = self._GetTestFilePath(['tsk_volume_system.raw'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    with self.assertRaises(errors.ScannerError):
      test_scanner._GetTSKPartitionIdentifiers(scan_node)

  @shared_test_lib.skipUnlessHasTestFile(['vsstest.qcow2'])
  def testGetVSSStoreIdentifiers(self):
    """Tests the _GetVSSStoreIdentifiers function."""
    # Test with mediator.
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    test_path = self._GetTestFilePath(['vsstest.qcow2'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    identifiers = test_scanner._GetVSSStoreIdentifiers(scan_node.sub_nodes[0])
    self.assertEqual(len(identifiers), 2)
    self.assertEqual(identifiers, ['vss1', 'vss2'])

    # Test without mediator.
    test_scanner = volume_scanner.VolumeScanner()

    test_path = self._GetTestFilePath(['vsstest.qcow2'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    with self.assertRaises(errors.ScannerError):
      test_scanner._GetVSSStoreIdentifiers(scan_node.sub_nodes[0])

    # Test error conditions.
    with self.assertRaises(errors.ScannerError):
      test_scanner._GetVSSStoreIdentifiers(None)

    scan_node = source_scanner.SourceScanNode(None)
    with self.assertRaises(errors.ScannerError):
      test_scanner._GetVSSStoreIdentifiers(scan_node)

  @shared_test_lib.skipUnlessHasTestFile(['tsk_volume_system.raw'])
  def testNormalizedVolumeIdentifiersPartitionedImage(self):
    """Tests the _NormalizedVolumeIdentifiers function."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    test_path = self._GetTestFilePath(['tsk_volume_system.raw'])
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
        volume_system, [1, 2], prefix='p')
    self.assertEqual(volume_identifiers, ['p1', 'p2'])

    # Test error conditions.
    with self.assertRaises(errors.ScannerError):
      test_scanner._NormalizedVolumeIdentifiers(
          volume_system, ['p3'], prefix='p')

  @shared_test_lib.skipUnlessHasTestFile(['vsstest.qcow2'])
  def testNormalizedVolumeIdentifiersVSS(self):
    """Tests the _NormalizedVolumeIdentifiers function on a VSS."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    test_path = self._GetTestFilePath(['vsstest.qcow2'])
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

  def testScanFileSystem(self):
    """Tests the _ScanFileSystem function."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    path_spec = fake_path_spec.FakePathSpec(location='/')
    scan_node = source_scanner.SourceScanNode(path_spec)

    base_path_specs = []
    test_scanner._ScanFileSystem(scan_node, base_path_specs)
    self.assertEqual(len(base_path_specs), 1)

    # Test error conditions.
    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanFileSystem(None, [])

    scan_node = source_scanner.SourceScanNode(None)
    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanFileSystem(scan_node, [])

  def testScanVolume(self):
    """Tests the _ScanVolume function."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    # Test error conditions.
    scan_context = source_scanner.SourceScannerContext()

    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanVolume(scan_context, None, [])

    volume_scan_node = source_scanner.SourceScanNode(None)
    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanVolume(scan_context, volume_scan_node, [])

  @shared_test_lib.skipUnlessHasTestFile(['apfs.dmg'])
  def testScanVolumeOnAPFS(self):
    """Tests the _ScanVolume function on an APFS image."""
    resolver.Resolver.key_chain.Empty()

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    test_path = self._GetTestFilePath(['apfs.dmg'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    volume_scan_node = self._GetTestScanNode(scan_context)

    apfs_container_scan_node = volume_scan_node.sub_nodes[4].sub_nodes[0]

    base_path_specs = []
    test_scanner._ScanVolume(
        scan_context, apfs_container_scan_node, base_path_specs)
    self.assertEqual(len(base_path_specs), 1)

  @shared_test_lib.skipUnlessHasTestFile(['bdetogo.raw'])
  def testScanVolumeOnBDE(self):
    """Tests the _ScanVolume function on a BDE image."""
    resolver.Resolver.key_chain.Empty()

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    test_path = self._GetTestFilePath(['bdetogo.raw'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    volume_scan_node = self._GetTestScanNode(scan_context)

    base_path_specs = []
    test_scanner._ScanVolume(
        scan_context, volume_scan_node.sub_nodes[0], base_path_specs)
    self.assertEqual(len(base_path_specs), 1)

  @shared_test_lib.skipUnlessHasTestFile(['ímynd.dd'])
  def testScanVolumeOnRAW(self):
    """Tests the _ScanVolume function on a RAW image."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    test_path = self._GetTestFilePath(['ímynd.dd'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    volume_scan_node = scan_context.GetRootScanNode()

    base_path_specs = []
    test_scanner._ScanVolume(scan_context, volume_scan_node, base_path_specs)
    self.assertEqual(len(base_path_specs), 1)

  @shared_test_lib.skipUnlessHasTestFile(['vsstest.qcow2'])
  def testScanVolumeOnVSS(self):
    """Tests the _ScanVolume function on VSS."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    test_path = self._GetTestFilePath(['vsstest.qcow2'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    volume_scan_node = self._GetTestScanNode(scan_context)

    base_path_specs = []
    test_scanner._ScanVolume(
        scan_context, volume_scan_node, base_path_specs)
    self.assertEqual(len(base_path_specs), 3)

  def testScanVolumeScanNode(self):
    """Tests the _ScanVolumeScanNode function."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    # Test error conditions.
    scan_context = source_scanner.SourceScannerContext()

    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanVolumeScanNode(scan_context, None, [])

    volume_scan_node = source_scanner.SourceScanNode(None)
    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanVolumeScanNode(scan_context, volume_scan_node, [])

  @shared_test_lib.skipUnlessHasTestFile(['apfs.dmg'])
  def testScanVolumeScanNodeOnAPFS(self):
    """Tests the _ScanVolumeScanNode function on an APFS image."""
    resolver.Resolver.key_chain.Empty()

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    test_path = self._GetTestFilePath(['apfs.dmg'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    volume_scan_node = self._GetTestScanNode(scan_context)

    apfs_container_scan_node = volume_scan_node.sub_nodes[4].sub_nodes[0]

    base_path_specs = []
    test_scanner._ScanVolumeScanNode(
        scan_context, apfs_container_scan_node, base_path_specs)
    self.assertEqual(len(base_path_specs), 1)

  @shared_test_lib.skipUnlessHasTestFile(['bdetogo.raw'])
  def testScanVolumeScanNodeOnBDE(self):
    """Tests the _ScanVolumeScanNode function on a BDE image."""
    resolver.Resolver.key_chain.Empty()

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    test_path = self._GetTestFilePath(['bdetogo.raw'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    volume_scan_node = self._GetTestScanNode(scan_context)

    base_path_specs = []
    test_scanner._ScanVolumeScanNode(
        scan_context, volume_scan_node.sub_nodes[0], base_path_specs)
    self.assertEqual(len(base_path_specs), 1)

  @shared_test_lib.skipUnlessHasTestFile(['ímynd.dd'])
  def testScanVolumeScanNodeOnRAW(self):
    """Tests the _ScanVolumeScanNode function on a RAW image."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    test_path = self._GetTestFilePath(['ímynd.dd'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    volume_scan_node = scan_context.GetRootScanNode()

    base_path_specs = []
    test_scanner._ScanVolumeScanNode(
        scan_context, volume_scan_node, base_path_specs)
    self.assertEqual(len(base_path_specs), 1)

  @shared_test_lib.skipUnlessHasTestFile(['vsstest.qcow2'])
  def testScanVolumeScanNodeOnVSS(self):
    """Tests the _ScanVolumeScanNode function on VSS."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    # Test function on VSS root.
    test_path = self._GetTestFilePath(['vsstest.qcow2'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    volume_scan_node = self._GetTestScanNode(scan_context)

    base_path_specs = []
    test_scanner._ScanVolumeScanNode(
        scan_context, volume_scan_node, base_path_specs)
    self.assertEqual(len(base_path_specs), 0)

    # Test function on VSS volume.
    test_path = self._GetTestFilePath(['vsstest.qcow2'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    volume_scan_node = self._GetTestScanNode(scan_context)

    base_path_specs = []
    test_scanner._ScanVolumeScanNode(
        scan_context, volume_scan_node.sub_nodes[0], base_path_specs)
    self.assertEqual(len(base_path_specs), 2)

  @shared_test_lib.skipUnlessHasTestFile(['vsstest.qcow2'])
  def testScanVolumeScanNodeVSS(self):
    """Tests the _ScanVolumeScanNodeVSS function."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    # Test function on VSS root.
    test_path = self._GetTestFilePath(['vsstest.qcow2'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    volume_scan_node = scan_context.GetRootScanNode()

    base_path_specs = []
    test_scanner._ScanVolumeScanNodeVSS(volume_scan_node, base_path_specs)
    self.assertEqual(len(base_path_specs), 0)

    # Test function on VSS volume.
    test_path = self._GetTestFilePath(['vsstest.qcow2'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_path)

    test_scanner._source_scanner.Scan(scan_context)
    volume_scan_node = self._GetTestScanNode(scan_context)

    base_path_specs = []
    test_scanner._ScanVolumeScanNodeVSS(
        volume_scan_node.sub_nodes[0], base_path_specs)
    self.assertEqual(len(base_path_specs), 2)

    # Test error conditions.
    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanVolumeScanNodeVSS(None, [])

    volume_scan_node = source_scanner.SourceScanNode(None)
    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanVolumeScanNodeVSS(volume_scan_node, [])

  # TODO: add tests for _UnlockEncryptedVolumeScanNode

  @shared_test_lib.skipUnlessHasTestFile(['ímynd.dd'])
  def testGetBasePathSpecsOnRAW(self):
    """Tests the GetBasePathSpecs function on a RAW image."""
    test_path = self._GetTestFilePath(['ímynd.dd'])
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

  @shared_test_lib.skipUnlessHasTestFile(['tsk_volume_system.raw'])
  def testGetBasePathSpecsOnPartitionedImage(self):
    """Tests the GetBasePathSpecs function on a partitioned image."""
    test_path = self._GetTestFilePath(['tsk_volume_system.raw'])
    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    test_tsk_partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/p2', part_index=6,
        start_offset=0x0002c000, parent=test_raw_path_spec)
    test_tsk_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/',
        parent=test_tsk_partition_path_spec)

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    expected_base_path_specs = [test_tsk_path_spec.comparable]

    base_path_specs = test_scanner.GetBasePathSpecs(test_path)
    base_path_specs = [
        base_path_spec.comparable for base_path_spec in base_path_specs]

    self.assertEqual(base_path_specs, expected_base_path_specs)

  @shared_test_lib.skipUnlessHasTestFile(['testdir_os'])
  def testGetBasePathSpecsOnDirectory(self):
    """Tests the GetBasePathSpecs function on a directory."""
    test_path = self._GetTestFilePath(['testdir_os'])
    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(mediator=test_mediator)

    expected_base_path_specs = [test_os_path_spec.comparable]

    base_path_specs = test_scanner.GetBasePathSpecs(test_path)
    base_path_specs = [
        base_path_spec.comparable for base_path_spec in base_path_specs]

    self.assertEqual(base_path_specs, expected_base_path_specs)


@shared_test_lib.skipUnlessHasTestFile(['windows_volume.qcow2'])
class WindowsVolumeScannerTest(shared_test_lib.BaseTestCase):
  """Tests for a Windows volume scanner."""

  # pylint: disable=protected-access

  def testScanFileSystem(self):
    """Tests the _ScanFileSystem function."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.WindowsVolumeScanner(mediator=test_mediator)

    test_path = self._GetTestFilePath(['windows_volume.qcow2'])
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

    with self.assertRaises(IOError):
      test_scanner.OpenFile('C:\\Windows\\System32\\config')

  @shared_test_lib.skipUnlessHasTestFile(['tsk_volume_system.raw'])
  def testScanForWindowsVolume(self):
    """Tests the ScanForWindowsVolume function."""
    test_path = self._GetTestFilePath(['tsk_volume_system.raw'])

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.WindowsVolumeScanner(mediator=test_mediator)

    result = test_scanner.ScanForWindowsVolume(test_path)
    self.assertFalse(result)

    test_path = self._GetTestFilePath(['windows_volume.qcow2'])

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.WindowsVolumeScanner(mediator=test_mediator)

    result = test_scanner.ScanForWindowsVolume(test_path)
    self.assertTrue(result)


if __name__ == '__main__':
  unittest.main()
