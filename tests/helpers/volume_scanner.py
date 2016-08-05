#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the volume scanner objects."""

import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import raw_path_spec
from dfvfs.path import tsk_partition_path_spec
from dfvfs.path import tsk_path_spec
from dfvfs.helpers import volume_scanner

from tests import test_lib as shared_test_lib


class VolumeScannerTest(shared_test_lib.BaseTestCase):
  """The unit test for the volume scanner object."""

  # TODO: add test for _GetTSKPartitionIdentifiers.
  # TODO: add test for _GetVSSStoreIdentifiers.
  # TODO: add test for _ScanFileSystem.
  # TODO: add test for _ScanVolume.
  # TODO: add test for _ScanVolumeScanNode.
  # TODO: add test for _ScanVolumeScanNodeEncrypted.
  # TODO: add test for _ScanVolumeScanNodeVSS.

  @shared_test_lib.skipUnlessHasTestFile([u'tsk_volume_system.raw'])
  def testGetBasePathSpecs(self):
    """Test the GetBasePathSpecs() function."""
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


class WindowsVolumeScannerTest(shared_test_lib.BaseTestCase):
  """The unit test for the Windows volume scanner object."""

  # TODO: add test for _ScanFileSystem.
  # TODO: add test for _ScanFileSystemForWindowsDirectory.
  # TODO: add test for OpenFile.

  @shared_test_lib.skipUnlessHasTestFile([u'tsk_volume_system.raw'])
  def testScanForWindowsVolume(self):
    """Test the ScanForWindowsVolume() function."""
    test_file = self._GetTestFilePath([u'tsk_volume_system.raw'])
    test_scanner = volume_scanner.WindowsVolumeScanner()

    result = test_scanner.ScanForWindowsVolume(test_file)
    self.assertFalse(result)

    # TODO: Add test that results in true.


if __name__ == '__main__':
  unittest.main()
