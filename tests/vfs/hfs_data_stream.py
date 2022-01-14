#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the data stream implementation using pyfshfs."""

import unittest

from dfvfs.vfs import hfs_data_stream

from tests import test_lib as shared_test_lib


class HFSDataStreamTest(shared_test_lib.BaseTestCase):
  """Tests the HFS data stream."""

  def testName(self):
    """Test the name property."""
    test_data_stream = hfs_data_stream.HFSDataStream(None)
    self.assertEqual(test_data_stream.name, '')

  def testIsDefault(self):
    """Test the IsDefault function."""
    test_data_stream = hfs_data_stream.HFSDataStream(None)
    result = test_data_stream.IsDefault()
    self.assertTrue(result)


if __name__ == '__main__':
  unittest.main()
