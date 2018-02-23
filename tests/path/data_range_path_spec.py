#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the data range path specification implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import data_range_path_spec

from tests.path import test_lib


class DataRangePathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the data range path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = data_range_path_spec.DataRangePathSpec(
        range_offset=0x2000, range_size=0x1000, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      data_range_path_spec.DataRangePathSpec(
          range_offset=0x2000, range_size=0x1000, parent=None)

    with self.assertRaises(ValueError):
      data_range_path_spec.DataRangePathSpec(
          range_offset=0x2000, range_size=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      data_range_path_spec.DataRangePathSpec(
          range_offset=None, range_size=0x1000, parent=self._path_spec)

    with self.assertRaises(ValueError):
      data_range_path_spec.DataRangePathSpec(
          range_offset=None, range_size=0x1000, parent=self._path_spec,
          bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = data_range_path_spec.DataRangePathSpec(
        range_offset=0x2000, range_size=0x1000, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: DATA_RANGE, range_offset: 0x00002000, range_size: 0x00001000',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
