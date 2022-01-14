#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the VFS data stream interface."""

import unittest

from dfvfs.vfs import data_stream

from tests import test_lib as shared_test_lib


class DataStreamTest(shared_test_lib.BaseTestCase):
  """Tests the VFS data stream interface."""

  def testName(self):
    """Test the name property."""
    test_data_stream = data_stream.DataStream(None)
    self.assertEqual(test_data_stream.name, '')

  def testGetExtents(self):
    """Test the GetExtents function."""
    test_data_stream = data_stream.DataStream(None)
    extents = test_data_stream.GetExtents()
    self.assertEqual(extents, [])

  def testIsDefault(self):
    """Test the IsDefault function."""
    test_data_stream = data_stream.DataStream(None)
    result = test_data_stream.IsDefault()
    self.assertTrue(result)


if __name__ == '__main__':
  unittest.main()
