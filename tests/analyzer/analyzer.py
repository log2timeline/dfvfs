#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Virtual File System (VFS) format analyzer."""

import unittest
import os

from dfvfs.analyzer import analyzer
from dfvfs.lib import definitions
from dfvfs.path import gzip_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import vshadow_path_spec


class AnalyzerTest(unittest.TestCase):
  """Class to test the analyzer."""

  def testGetArchiveTypeIndicators(self):
    """Function to test the get archive type indicators function."""
    test_file = os.path.join(u'test_data', u'syslog.tar')
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_TAR]
    type_indicators = analyzer.Analyzer.GetArchiveTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

    test_file = os.path.join(u'test_data', u'syslog.zip')
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_ZIP]
    type_indicators = analyzer.Analyzer.GetArchiveTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  def testGetCompressedStreamTypeIndicators(self):
    """Function to test the get compressed stream type indicators function."""
    test_file = os.path.join(u'test_data', u'syslog.gz')
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_GZIP]
    type_indicators = analyzer.Analyzer.GetCompressedStreamTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  def testGetCompressedArchiveTypeIndicators(self):
    """Function to test the get compressed archive type indicators function."""
    test_file = os.path.join(u'test_data', u'syslog.tgz')
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

  def testGetFileSystemTypeIndicators(self):
    """Function to test the get file system type indicators function."""
    test_file = os.path.join(u'test_data', u'vsstest.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=path_spec)

    expected_type_indicators = [definitions.PREFERRED_NTFS_BACK_END]
    type_indicators = analyzer.Analyzer.GetFileSystemTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  def testGetStorageMediaImageTypeIndicators(self):
    """Function to test the get image type indicators function."""
    test_file = os.path.join(u'test_data', u'image.E01')
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_EWF]
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

    test_file = os.path.join(u'test_data', u'image.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_QCOW]
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

    test_file = os.path.join(u'test_data', u'image.vhd')
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_VHDI]
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

    test_file = os.path.join(u'test_data', u'image.vmdk')
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_VMDK]
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

    test_file = os.path.join(u'test_data', u'mactime.body')
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = []
    type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

  def testGetVolumeSystemTypeIndicators(self):
    """Function to test the get volume system type indicators function."""
    test_file = os.path.join(u'test_data', u'tsk_volume_system.raw')
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_TSK_PARTITION]
    type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

    test_file = os.path.join(u'test_data', u'vsstest.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)

    expected_type_indicators = [definitions.TYPE_INDICATOR_VSHADOW]
    type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)

    test_file = os.path.join(u'test_data', u'bdetogo.raw')
    path_spec = os_path_spec.OSPathSpec(location=test_file)

    expected_type_indicators = [definitions.TYPE_INDICATOR_BDE]
    type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
        path_spec)
    self.assertEqual(type_indicators, expected_type_indicators)


if __name__ == '__main__':
  unittest.main()
