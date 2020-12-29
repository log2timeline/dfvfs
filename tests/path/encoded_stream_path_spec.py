#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the encoded stream path specification implementation."""

import unittest

from dfvfs.path import encoded_stream_path_spec

from tests.path import test_lib


class EncodedStreamPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the encoded stream path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = encoded_stream_path_spec.EncodedStreamPathSpec(
        encoding_method='test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      encoded_stream_path_spec.EncodedStreamPathSpec(
          encoding_method='test', parent=None)

    with self.assertRaises(ValueError):
      encoded_stream_path_spec.EncodedStreamPathSpec(
          encoding_method=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      encoded_stream_path_spec.EncodedStreamPathSpec(
          encoding_method='test', parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = encoded_stream_path_spec.EncodedStreamPathSpec(
        encoding_method='test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: ENCODED_STREAM, encoding_method: test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
