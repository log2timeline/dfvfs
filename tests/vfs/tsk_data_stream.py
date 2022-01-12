#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the data stream implementation using pytsk3."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import tsk_data_stream
from dfvfs.vfs import tsk_file_system

from tests import test_lib as shared_test_lib


class TSKDataStreamTest(shared_test_lib.BaseTestCase):
  """Tests the SleuthKit (TSK) data stream."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['ext2.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._tsk_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/',
        parent=self._raw_path_spec)

    self._file_system = tsk_file_system.TSKFileSystem(
        self._resolver_context, self._tsk_path_spec)
    self._file_system.Open()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testName(self):
    """Test the name property."""
    test_data_stream = tsk_data_stream.TSKDataStream(
        self._file_system, None)
    self.assertEqual(test_data_stream.name, '')

  def testIsDefault(self):
    """Test the IsDefault function."""
    test_data_stream = tsk_data_stream.TSKDataStream(
        self._file_system, None)
    self.assertTrue(test_data_stream.IsDefault())


if __name__ == '__main__':
  unittest.main()
