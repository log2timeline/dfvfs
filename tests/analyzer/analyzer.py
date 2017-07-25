#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Virtual File System (VFS) format analyzer."""

from __future__ import unicode_literals

import unittest

from dfvfs.analyzer import analyzer
from dfvfs.lib import definitions
from dfvfs.path import gzip_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import tsk_partition_path_spec
from dfvfs.path import vshadow_path_spec

from tests import test_lib as shared_test_lib


class AnalyzerTest(shared_test_lib.BaseTestCase):
  """Class to test the analyzer."""

  @shared_test_lib.skipUnlessHasTestFile(['syslog.tar'])
  def testGetArchiveTypeIndicatorsTAR(self):
    """Function to test the get archive type indicators function."""
    test_file = self._GetTestFilePath(['syslog.tar'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_TAR]
    type_indicators = analyzer.Analyzer.GetArchiveTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['syslog.zip'])
  def testGetArchiveTypeIndicatorsZIP(self):
    """Function to test the get archive type indicators function."""
    test_file = self._GetTestFilePath(['syslog.zip'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_ZIP]
    type_indicators = analyzer.Analyzer.GetArchiveTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['syslog.gz'])
  def testGetCompressedStreamTypeIndicatorsGZIP(self):
    """Function to test the get compressed stream type indicators function."""
    test_file = self._GetTestFilePath(['syslog.gz'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_GZIP]
    type_indicators = analyzer.Analyzer.GetCompressedStreamTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['syslog.tgz'])
  def testGetCompressedArchiveTypeIndicators(self):
    """Function to test the get compressed archive type indicators function."""
    test_file = self._GetTestFilePath(['syslog.tgz'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_GZIP]
    type_indicators = analyzer.Analyzer.GetCompressedStreamTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

    path_spec = gzip_path_spec.GzipPathSpec(parent=path_spec)

    expected_type_indicators = [definitions.TYPE_INDICATOR_TAR]
    type_indicators = analyzer.Analyzer.GetArchiveTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['vsstest.qcow2'])
  def testGetFileSystemTypeIndicators(self):
    """Function to test the get file system type indicators function."""
    test_file = self._GetTestFilePath(['vsstest.qcow2'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=path_spec)

    expected_type_indicators = [definitions.PREFERRED_NTFS_BACK_END]
    type_indicators = analyzer.Analyzer.GetFileSystemTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['image.E01'])
  def testGetStorageMediaImageTypeIndicatorsEWF(self):
    """Function to test the get image type indicators function."""
    test_file = self._GetTestFilePath(['image.E01'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_EWF]
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['image.qcow2'])
  def testGetStorageMediaImageTypeIndicatorsQCOW(self):
    """Function to test the get image type indicators function."""
    test_file = self._GetTestFilePath(['image.qcow2'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_QCOW]
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['image.vhd'])
  def testGetStorageMediaImageTypeIndicatorsVHDI(self):
    """Function to test the get image type indicators function."""
    test_file = self._GetTestFilePath(['image.vhd'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_VHDI]
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['image.vmdk'])
  def testGetStorageMediaImageTypeIndicatorsVMDK(self):
    """Function to test the get image type indicators function."""
    test_file = self._GetTestFilePath(['image.vmdk'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_VMDK]
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['mactime.body'])
  def testGetStorageMediaImageTypeIndicatorsBodyFile(self):
    """Function to test the get image type indicators function."""
    test_file = self._GetTestFilePath(['mactime.body'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = []
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['tsk_volume_system.raw'])
  def testGetVolumeSystemTypeIndicatorsTSK(self):
    """Function to test the get volume system type indicators function."""
    test_file = self._GetTestFilePath(['tsk_volume_system.raw'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_TSK_PARTITION]
    type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['vsstest.qcow2'])
  def testGetVolumeSystemTypeIndicatorsVSS(self):
    """Function to test the get volume system type indicators function."""
    test_file = self._GetTestFilePath(['vsstest.qcow2'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)

    expected_type_indicators = [definitions.TYPE_INDICATOR_VSHADOW]
    type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['bdetogo.raw'])
  def testGetVolumeSystemTypeIndicatorsBDE(self):
    """Function to test the get volume system type indicators function."""
    test_file = self._GetTestFilePath(['bdetogo.raw'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_BDE]
    type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['fvdetest.qcow2'])
  def testGetVolumeSystemTypeIndicatorsFVDE(self):
    """Function to test the get volume system type indicators function."""
    test_file = self._GetTestFilePath(['fvdetest.qcow2'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p1', parent=path_spec)

    expected_type_indicators = [definitions.TYPE_INDICATOR_FVDE]
    type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)


if __name__ == '__main__':
  unittest.main()
