#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the compressed stream path specification implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import compressed_stream_path_spec

from tests.path import test_lib


class CompressedStreamPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the compressed stream path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = compressed_stream_path_spec.CompressedStreamPathSpec(
        compression_method='test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      compressed_stream_path_spec.CompressedStreamPathSpec(
          compression_method='test', parent=None)

    with self.assertRaises(ValueError):
      compressed_stream_path_spec.CompressedStreamPathSpec(
          compression_method=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      compressed_stream_path_spec.CompressedStreamPathSpec(
          compression_method='test', parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = compressed_stream_path_spec.CompressedStreamPathSpec(
        compression_method='test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: COMPRESSED_STREAM, compression_method: test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
