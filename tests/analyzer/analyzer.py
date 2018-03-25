#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the format analyzer."""

from __future__ import unicode_literals

import unittest

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions
from dfvfs.path import gzip_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import tsk_partition_path_spec
from dfvfs.path import vshadow_path_spec

from tests import test_lib as shared_test_lib


class TestAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Analyzer helper for testing."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_VOLUME_SYSTEM])

  TYPE_INDICATOR = 'test'

  def AnalyzeFileObject(self, unused_file_object):
    """Retrieves the format specification.

    This is the fall through implementation that raises a RuntimeError.

    Args:
      unused_file_object (FileIO): file-like object.

    Returns:
      str: type indicator if the file-like object contains a supported format
          or None otherwise.
    """
    return


class AnalyzerTest(shared_test_lib.BaseTestCase):
  """Tests for the format analyzer."""

  # pylint: disable=protected-access

  def testFlushCache(self):
    """Tests the _FlushCache function."""
    analyzer.Analyzer._FlushCache(definitions.FORMAT_CATEGORIES)

  def testGetSignatureScanner(self):
    """Tests the _GetSignatureScanner function."""
    specification_store = specification.FormatSpecificationStore()

    signature_scanner = analyzer.Analyzer._GetSignatureScanner(
        specification_store)
    self.assertIsNotNone(signature_scanner)

  def testGetSpecificationStore(self):
    """Tests the _GetSpecificationStore function."""
    specification_store = analyzer.Analyzer._GetSpecificationStore(
        definitions.FORMAT_CATEGORY_VOLUME_SYSTEM)
    self.assertIsNotNone(specification_store)

  # TODO: add tests for _GetTypeIndicators

  def testHelperRegistration(self):
    """Tests the DeregisterHelper and RegisterHelper functions."""
    test_helper = TestAnalyzerHelper()

    number_of_helpers = len(analyzer.Analyzer._analyzer_helpers)

    analyzer.Analyzer.RegisterHelper(test_helper)
    self.assertEqual(
        len(analyzer.Analyzer._analyzer_helpers), number_of_helpers + 1)

    with self.assertRaises(KeyError):
      analyzer.Analyzer.RegisterHelper(test_helper)

    analyzer.Analyzer.DeregisterHelper(test_helper)
    self.assertEqual(
        len(analyzer.Analyzer._analyzer_helpers), number_of_helpers)

  @shared_test_lib.skipUnlessHasTestFile(['syslog.tar'])
  def testGetArchiveTypeIndicatorsTAR(self):
    """Tests the GetArchiveTypeIndicators function on a .tar file."""
    test_file = self._GetTestFilePath(['syslog.tar'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_TAR]
    type_indicators = analyzer.Analyzer.GetArchiveTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['syslog.zip'])
  def testGetArchiveTypeIndicatorsZIP(self):
    """Tests the GetArchiveTypeIndicators function on a .zip file."""
    test_file = self._GetTestFilePath(['syslog.zip'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_ZIP]
    type_indicators = analyzer.Analyzer.GetArchiveTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['syslog.gz'])
  def testGetCompressedStreamTypeIndicatorsGZIP(self):
    """Tests the GetCompressedStreamTypeIndicators function on a .gz file."""
    test_file = self._GetTestFilePath(['syslog.gz'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_GZIP]
    type_indicators = analyzer.Analyzer.GetCompressedStreamTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['syslog.tgz'])
  def testGetCompressedArchiveTypeIndicators(self):
    """Tests the GetCompressedStreamTypeIndicators function on a .tgz file."""
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
    """Tests the GetFileSystemTypeIndicators function on a .qcow2 file."""
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
    """Tests the GetStorageMediaImageTypeIndicator function on a .E01 file."""
    test_file = self._GetTestFilePath(['image.E01'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_EWF]
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['image.qcow2'])
  def testGetStorageMediaImageTypeIndicatorsQCOW(self):
    """Tests the GetStorageMediaImageTypeIndicator function on a .qcow2 file."""
    test_file = self._GetTestFilePath(['image.qcow2'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_QCOW]
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['image.vhd'])
  def testGetStorageMediaImageTypeIndicatorsVHDI(self):
    """Tests the GetStorageMediaImageTypeIndicator function on a .vhd file."""
    test_file = self._GetTestFilePath(['image.vhd'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_VHDI]
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['image.vmdk'])
  def testGetStorageMediaImageTypeIndicatorsVMDK(self):
    """Tests the GetStorageMediaImageTypeIndicator function on a .vmdk file."""
    test_file = self._GetTestFilePath(['image.vmdk'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_VMDK]
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['mactime.body'])
  def testGetStorageMediaImageTypeIndicatorsBodyFile(self):
    """Tests the GetStorageMediaImageTypeIndicator function on a bodyfile."""
    test_file = self._GetTestFilePath(['mactime.body'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = []
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['tsk_volume_system.raw'])
  def testGetVolumeSystemTypeIndicatorsTSK(self):
    """Tests the GetVolumeSystemTypeIndicators function on partitions."""
    test_file = self._GetTestFilePath(['tsk_volume_system.raw'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_TSK_PARTITION]
    type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['vsstest.qcow2'])
  def testGetVolumeSystemTypeIndicatorsVSS(self):
    """Tests the GetVolumeSystemTypeIndicators function on a VSS volume."""
    test_file = self._GetTestFilePath(['vsstest.qcow2'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)

    expected_type_indicators = [definitions.TYPE_INDICATOR_VSHADOW]
    type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['bdetogo.raw'])
  def testGetVolumeSystemTypeIndicatorsBDE(self):
    """Tests the GetVolumeSystemTypeIndicators function on a BDE ToGo drive."""
    test_file = self._GetTestFilePath(['bdetogo.raw'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_BDE]
    type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  @shared_test_lib.skipUnlessHasTestFile(['fvdetest.qcow2'])
  def testGetVolumeSystemTypeIndicatorsFVDE(self):
    """Tests the GetVolumeSystemTypeIndicators function on a FVDE volume."""
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
