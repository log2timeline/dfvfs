#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the data stream implementation using pytsk3."""

import unittest

from dfvfs.vfs import tsk_data_stream

from tests import test_lib as shared_test_lib


class TSKDataStreamTest(shared_test_lib.BaseTestCase):
  """Tests the SleuthKit (TSK) data stream."""

  def testName(self):
    """Test the name property."""
    test_data_stream = tsk_data_stream.TSKDataStream(None)
    self.assertEqual(test_data_stream.name, '')

  def testIsDefault(self):
    """Test the IsDefault function."""
    test_data_stream = tsk_data_stream.TSKDataStream(None)
    self.assertTrue(test_data_stream.IsDefault())


if __name__ == '__main__':
  unittest.main()
