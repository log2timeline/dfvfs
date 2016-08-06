#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Virtual File System (VFS) format analyzer."""

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

  @shared_test_lib.skipUnlessHasTestFile([u'syslog.tar'])
  def testGetArchiveTypeIndicatorsTAR(self):
    """Function to test the get archive type indicators function."""
    test_file = self._GetTestFilePath([u'syslog.tar'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_TAR]
    type_indicators = analyzer.Analyzer.GetArchiveTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile([u'syslog.zip'])
  def testGetArchiveTypeIndicatorsZIP(self):
    """Function to test the get archive type indicators function."""
    test_file = self._GetTestFilePath([u'syslog.zip'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_ZIP]
    type_indicators = analyzer.Analyzer.GetArchiveTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile([u'syslog.gz'])
  def testGetCompressedStreamTypeIndicatorsGZIP(self):
    """Function to test the get compressed stream type indicators function."""
    test_file = self._GetTestFilePath([u'syslog.gz'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_GZIP]
    type_indicators = analyzer.Analyzer.GetCompressedStreamTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile([u'syslog.tgz'])
  def testGetCompressedArchiveTypeIndicators(self):
    """Function to test the get compressed archive type indicators function."""
    test_file = self._GetTestFilePath([u'syslog.tgz'])
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

  @shared_test_lib.skipUnlessHasTestFile([u'vsstest.qcow2'])
  def testGetFileSystemTypeIndicators(self):
    """Function to test the get file system type indicators function."""
    test_file = self._GetTestFilePath([u'vsstest.qcow2'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=path_spec)

    expected_type_indicators = [definitions.PREFERRED_NTFS_BACK_END]
    type_indicators = analyzer.Analyzer.GetFileSystemTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile([u'image.E01'])
  def testGetStorageMediaImageTypeIndicatorsEWF(self):
    """Function to test the get image type indicators function."""
    test_file = self._GetTestFilePath([u'image.E01'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_EWF]
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile([u'image.qcow2'])
  def testGetStorageMediaImageTypeIndicatorsQCOW(self):
    """Function to test the get image type indicators function."""
    test_file = self._GetTestFilePath([u'image.qcow2'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_QCOW]
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile([u'image.vhd'])
  def testGetStorageMediaImageTypeIndicatorsVHDI(self):
    """Function to test the get image type indicators function."""
    test_file = self._GetTestFilePath([u'image.vhd'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_VHDI]
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile([u'image.vmdk'])
  def testGetStorageMediaImageTypeIndicatorsVMDK(self):
    """Function to test the get image type indicators function."""
    test_file = self._GetTestFilePath([u'image.vmdk'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_VMDK]
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile([u'mactime.body'])
  def testGetStorageMediaImageTypeIndicatorsBodyFile(self):
    """Function to test the get image type indicators function."""
    test_file = self._GetTestFilePath([u'mactime.body'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = []
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile([u'tsk_volume_system.raw'])
  def testGetVolumeSystemTypeIndicatorsTSK(self):
    """Function to test the get volume system type indicators function."""
    test_file = self._GetTestFilePath([u'tsk_volume_system.raw'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_TSK_PARTITION]
    type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile([u'vsstest.qcow2'])
  def testGetVolumeSystemTypeIndicatorsVSS(self):
    """Function to test the get volume system type indicators function."""
    test_file = self._GetTestFilePath([u'vsstest.qcow2'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)

    expected_type_indicators = [definitions.TYPE_INDICATOR_VSHADOW]
    type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile([u'bdetogo.raw'])
  def testGetVolumeSystemTypeIndicatorsBDE(self):
    """Function to test the get volume system type indicators function."""
    test_file = self._GetTestFilePath([u'bdetogo.raw'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_BDE]
    type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile([u'fvdetest.qcow2'])
  def testGetVolumeSystemTypeIndicatorsFVDE(self):
    """Function to test the get volume system type indicators function."""
    test_file = self._GetTestFilePath([u'fvdetest.qcow2'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=u'/p1', parent=path_spec)

    expected_type_indicators = [definitions.TYPE_INDICATOR_FVDE]
    type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)


if __name__ == '__main__':
  unittest.main()
