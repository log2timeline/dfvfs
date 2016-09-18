#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the volume scanner objects."""

import unittest

from dfvfs.lib import errors
from dfvfs.path import fake_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import raw_path_spec
from dfvfs.path import tsk_partition_path_spec
from dfvfs.path import tsk_path_spec
from dfvfs.helpers import source_scanner
from dfvfs.helpers import volume_scanner
from dfvfs.resolver import resolver

from tests import test_lib as shared_test_lib


class TestVolumeScannerMediator(volume_scanner.VolumeScannerMediator):
  """Class that defines a volume scanner mediator for testing."""

  _BDE_PASSWORD = u'bde-TEST'

  def GetPartitionIdentifiers(self, unused_volume_system, volume_identifiers):
    """Retrieves partition identifiers.

    This method can be used to prompt the user to provide partition identifiers.

    Args:
      volume_system (TSKVolumeSystem): volume system.
      volume_identifiers (list[str]): volume identifiers.

    Returns:
      list[str]: selected partition identifiers, such as "p1", or None.

    Raises:
      ScannerError: if the source cannot be processed.
    """
    return volume_identifiers

  def GetVSSStoreIdentifiers(self, unused_volume_system, volume_identifiers):
    """Retrieves VSS store identifiers.

    This method can be used to prompt the user to provide VSS store identifiers.

    Args:
      volume_system (VShadowVolumeSystem): volume system.
      volume_identifiers (list[str]): volume identifiers.

    Returns:
      list[int]: selected VSS store numbers or None.

    Raises:
      ScannerError: if the source cannot be processed.
    """
    return [
        int(volume_identifier[3:], 10)
        for volume_identifier in volume_identifiers]

  def UnlockEncryptedVolume(
      self, source_scanner_object, scan_context, locked_scan_node,
      unused_credentials):
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
        scan_context, locked_scan_node.path_spec, u'password',
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

  @shared_test_lib.skipUnlessHasTestFile([u'tsk_volume_system.raw'])
  def testGetTSKPartitionIdentifiers(self):
    """Tests the _GetTSKPartitionIdentifiers function."""
    # Test with mediator.
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(test_mediator)

    test_file = self._GetTestFilePath([u'tsk_volume_system.raw'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    expected_identifiers = sorted([u'p1', u'p2'])
    identifiers = test_scanner._GetTSKPartitionIdentifiers(scan_node)
    self.assertEqual(len(identifiers), 2)
    self.assertEqual(sorted(identifiers), expected_identifiers)

    # Test without mediator.
    test_scanner = volume_scanner.VolumeScanner()

    test_file = self._GetTestFilePath([u'tsk_volume_system.raw'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    expected_identifiers = sorted([u'p1', u'p2'])
    identifiers = test_scanner._GetTSKPartitionIdentifiers(scan_node)
    self.assertEqual(len(identifiers), 2)
    self.assertEqual(sorted(identifiers), expected_identifiers)

    # Test error conditions.
    with self.assertRaises(errors.ScannerError):
      test_scanner._GetTSKPartitionIdentifiers(None)

    scan_node = source_scanner.SourceScanNode(None)
    with self.assertRaises(errors.ScannerError):
      test_scanner._GetTSKPartitionIdentifiers(scan_node)

  @shared_test_lib.skipUnlessHasTestFile([u'vsstest.qcow2'])
  def testGetVSSStoreIdentifiers(self):
    """Tests the _GetVSSStoreIdentifiers function."""
    # Test with mediator.
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(test_mediator)

    test_file = self._GetTestFilePath([u'vsstest.qcow2'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    test_scanner._source_scanner.Scan(scan_context)
    scan_node = self._GetTestScanNode(scan_context)

    expected_identifiers = sorted([1, 2])
    identifiers = test_scanner._GetVSSStoreIdentifiers(scan_node.sub_nodes[0])
    self.assertEqual(len(identifiers), 2)
    self.assertEqual(sorted(identifiers), expected_identifiers)

    # Test without mediator.
    test_scanner = volume_scanner.VolumeScanner()

    test_file = self._GetTestFilePath([u'vsstest.qcow2'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

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

  def testScanFileSystem(self):
    """Tests the _ScanFileSystem function."""
    test_scanner = volume_scanner.VolumeScanner()

    path_spec = fake_path_spec.FakePathSpec(location=u'/')
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

  @shared_test_lib.skipUnlessHasTestFile([u'ímynd.dd'])
  def testScanVolumeRAW(self):
    """Tests the _ScanVolume function on a RAW image."""
    test_scanner = volume_scanner.VolumeScanner()

    test_file = self._GetTestFilePath([u'ímynd.dd'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    test_scanner._source_scanner.Scan(scan_context)
    volume_scan_node = scan_context.GetRootScanNode()

    base_path_specs = []
    test_scanner._ScanVolume(scan_context, volume_scan_node, base_path_specs)
    self.assertEqual(len(base_path_specs), 1)

    # Test error conditions.
    scan_context = source_scanner.SourceScannerContext()

    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanVolume(scan_context, None, [])

    volume_scan_node = source_scanner.SourceScanNode(None)
    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanVolume(scan_context, volume_scan_node, [])

  @shared_test_lib.skipUnlessHasTestFile([u'vsstest.qcow2'])
  def testScanVolumeVSS(self):
    """Tests the _ScanVolume function on NSS."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(test_mediator)

    test_file = self._GetTestFilePath([u'vsstest.qcow2'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    test_scanner._source_scanner.Scan(scan_context)
    volume_scan_node = self._GetTestScanNode(scan_context)

    base_path_specs = []
    test_scanner._ScanVolume(
        scan_context, volume_scan_node, base_path_specs)
    self.assertEqual(len(base_path_specs), 3)

  @shared_test_lib.skipUnlessHasTestFile([u'ímynd.dd'])
  def testScanVolumeScanNodeRAW(self):
    """Tests the _ScanVolumeScanNode function on a RAW image."""
    test_scanner = volume_scanner.VolumeScanner()

    test_file = self._GetTestFilePath([u'ímynd.dd'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    test_scanner._source_scanner.Scan(scan_context)
    volume_scan_node = scan_context.GetRootScanNode()

    base_path_specs = []
    test_scanner._ScanVolumeScanNode(
        scan_context, volume_scan_node, base_path_specs)
    self.assertEqual(len(base_path_specs), 1)

    # Test error conditions.
    scan_context = source_scanner.SourceScannerContext()

    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanVolumeScanNode(scan_context, None, [])

    volume_scan_node = source_scanner.SourceScanNode(None)
    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanVolumeScanNode(scan_context, volume_scan_node, [])

  @shared_test_lib.skipUnlessHasTestFile([u'vsstest.qcow2'])
  def testScanVolumeScanNode(self):
    """Tests the _ScanVolumeScanNode function on VSS."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(test_mediator)

    # Test VSS root.
    test_file = self._GetTestFilePath([u'vsstest.qcow2'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    test_scanner._source_scanner.Scan(scan_context)
    volume_scan_node = self._GetTestScanNode(scan_context)

    base_path_specs = []
    test_scanner._ScanVolumeScanNode(
        scan_context, volume_scan_node, base_path_specs)
    self.assertEqual(len(base_path_specs), 0)

    # Test VSS volume.
    test_file = self._GetTestFilePath([u'vsstest.qcow2'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    test_scanner._source_scanner.Scan(scan_context)
    volume_scan_node = self._GetTestScanNode(scan_context)

    base_path_specs = []
    test_scanner._ScanVolumeScanNode(
        scan_context, volume_scan_node.sub_nodes[0], base_path_specs)
    self.assertEqual(len(base_path_specs), 2)

  @shared_test_lib.skipUnlessHasTestFile([u'bdetogo.raw'])
  def testScanVolumeScanNodeEncrypted(self):
    """Tests the _ScanVolumeScanNodeEncrypted function."""
    resolver.Resolver.key_chain.Empty()

    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(test_mediator)

    test_file = self._GetTestFilePath([u'bdetogo.raw'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    test_scanner._source_scanner.Scan(scan_context)
    volume_scan_node = self._GetTestScanNode(scan_context)

    base_path_specs = []
    test_scanner._ScanVolumeScanNode(
        scan_context, volume_scan_node.sub_nodes[0], base_path_specs)
    self.assertEqual(len(base_path_specs), 1)

    # Test error conditions.
    path_spec = fake_path_spec.FakePathSpec(location=u'/')
    scan_node = source_scanner.SourceScanNode(path_spec)

    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanVolumeScanNodeEncrypted(scan_node, None, [])

    volume_scan_node = source_scanner.SourceScanNode(None)
    with self.assertRaises(errors.ScannerError):
      test_scanner._ScanVolumeScanNodeEncrypted(scan_node, volume_scan_node, [])

  @shared_test_lib.skipUnlessHasTestFile([u'vsstest.qcow2'])
  def testScanVolumeScanNodeVSS(self):
    """Tests the _ScanVolumeScanNodeVSS function."""
    test_mediator = TestVolumeScannerMediator()
    test_scanner = volume_scanner.VolumeScanner(test_mediator)

    # Test root.
    test_file = self._GetTestFilePath([u'vsstest.qcow2'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

    test_scanner._source_scanner.Scan(scan_context)
    volume_scan_node = scan_context.GetRootScanNode()

    base_path_specs = []
    test_scanner._ScanVolumeScanNodeVSS(volume_scan_node, base_path_specs)
    self.assertEqual(len(base_path_specs), 0)

    # Test VSS volume.
    test_file = self._GetTestFilePath([u'vsstest.qcow2'])
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(test_file)

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

  @shared_test_lib.skipUnlessHasTestFile([u'ímynd.dd'])
  def testGetBasePathSpecsRAW(self):
    """Tests the GetBasePathSpecs function on a RAW image."""
    test_file = self._GetTestFilePath([u'ímynd.dd'])
    test_scanner = volume_scanner.VolumeScanner()

    test_os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    test_raw_path_spec = raw_path_spec.RawPathSpec(parent=test_os_path_spec)
    test_tsk_path_spec = tsk_path_spec.TSKPathSpec(
        location=u'/', parent=test_raw_path_spec)

    expected_base_path_specs = [test_tsk_path_spec.comparable]

    base_path_specs = test_scanner.GetBasePathSpecs(test_file)
    base_path_specs = [
        base_path_spec.comparable for base_path_spec in base_path_specs]

    self.assertEqual(base_path_specs, expected_base_path_specs)

    # Test error conditions.
    with self.assertRaises(errors.ScannerError):
      test_scanner.GetBasePathSpecs(None)

    with self.assertRaises(errors.ScannerError):
      test_scanner.GetBasePathSpecs(u'/bogus')

  @shared_test_lib.skipUnlessHasTestFile([u'tsk_volume_system.raw'])
  def testGetBasePathSpecsPartitionedImage(self):
    """Tests the GetBasePathSpecs function on a partitioned image."""
    test_file = self._GetTestFilePath([u'tsk_volume_system.raw'])
    test_scanner = volume_scanner.VolumeScanner()

    test_os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    test_raw_path_spec = raw_path_spec.RawPathSpec(parent=test_os_path_spec)
    test_tsk_partition_path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=u'/p2', part_index=6, start_offset=0x0002c000,
        parent=test_raw_path_spec)
    test_tsk_path_spec = tsk_path_spec.TSKPathSpec(
        location=u'/', parent=test_tsk_partition_path_spec)

    expected_base_path_specs = [test_tsk_path_spec.comparable]

    base_path_specs = test_scanner.GetBasePathSpecs(test_file)
    base_path_specs = [
        base_path_spec.comparable for base_path_spec in base_path_specs]

    self.assertEqual(base_path_specs, expected_base_path_specs)

  @shared_test_lib.skipUnlessHasTestFile([u'testdir_os'])
  def testGetBasePathSpecsDirectory(self):
    """Tests the GetBasePathSpecs function on a directory."""
    test_file = self._GetTestFilePath([u'testdir_os'])
    test_scanner = volume_scanner.VolumeScanner()

    test_os_path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_base_path_specs = [test_os_path_spec.comparable]

    base_path_specs = test_scanner.GetBasePathSpecs(test_file)
    base_path_specs = [
        base_path_spec.comparable for base_path_spec in base_path_specs]

    self.assertEqual(base_path_specs, expected_base_path_specs)


@shared_test_lib.skipUnlessHasTestFile([u'windows_volume.qcow2'])
class WindowsVolumeScannerTest(shared_test_lib.BaseTestCase):
  """Tests for a Windows volume scanner."""

  # pylint: disable=protected-access

  def testScanFileSystem(self):
    """Tests the _ScanFileSystem function."""
    test_scanner = volume_scanner.WindowsVolumeScanner()

    test_file = self._GetTestFilePath([u'windows_volume.qcow2'])
    test_os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    test_qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=test_os_path_spec)
    test_tsk_path_spec = tsk_path_spec.TSKPathSpec(
        location=u'/', parent=test_qcow_path_spec)
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
    test_file = self._GetTestFilePath([u'windows_volume.qcow2'])
    test_scanner = volume_scanner.WindowsVolumeScanner()

    result = test_scanner.ScanForWindowsVolume(test_file)
    self.assertTrue(result)

    file_object = test_scanner.OpenFile(
        u'C:\\Windows\\System32\\config\\syslog')
    self.assertIsNotNone(file_object)
    file_object.close()

    file_object = test_scanner.OpenFile(u'C:\\bogus')
    self.assertIsNone(file_object)

    with self.assertRaises(IOError):
      test_scanner.OpenFile(u'C:\\Windows\\System32\\config')

  @shared_test_lib.skipUnlessHasTestFile([u'tsk_volume_system.raw'])
  def testScanForWindowsVolume(self):
    """Tests the ScanForWindowsVolume function."""
    test_file = self._GetTestFilePath([u'tsk_volume_system.raw'])
    test_scanner = volume_scanner.WindowsVolumeScanner()

    result = test_scanner.ScanForWindowsVolume(test_file)
    self.assertFalse(result)

    test_file = self._GetTestFilePath([u'windows_volume.qcow2'])
    test_scanner = volume_scanner.WindowsVolumeScanner()

    result = test_scanner.ScanForWindowsVolume(test_file)
    self.assertTrue(result)


if __name__ == '__main__':
  unittest.main()
