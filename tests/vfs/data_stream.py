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
    test_data_stream = data_stream.DataStream()
    self.assertEqual(test_data_stream.name, '')

  def testIsDefault(self):
    """Test the IsDefault function."""
    test_data_stream = data_stream.DataStream()
    self.assertTrue(test_data_stream.IsDefault())


if __name__ == '__main__':
  unittest.main()
