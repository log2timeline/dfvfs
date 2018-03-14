#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the xz decompressor object."""

from __future__ import unicode_literals

import unittest

try:
  from dfvfs.compression import xz_decompressor
except ImportError:
  xz_decompressor = None

from dfvfs.lib import errors

from tests.compression import test_lib


@unittest.skipIf(xz_decompressor is None, 'requires LZMA compression support')
class LZMADecompressorTestCase(test_lib.DecompressorTestCase):
  """Tests for the lzma decompressor object."""

  def testDecompress(self):
    """Tests the Decompress method."""
    decompressor = xz_decompressor.LZMADecompressor()

    compressed_data = (
        b']\x00\x00\x80\x00\xff\xff\xff\xff\xff\xff\xff\xff\x00*\x1a\t\'d\x1c'
        b'\x87\x8aO\xcaL\xf4\xf8!\xda\x88\xd8\xff\xff\xeb\xcc\x00')

    uncompressed_data, _ = decompressor.Decompress(compressed_data)
    expected_uncompressed_data = b'This is a test.'
    self.assertEqual(uncompressed_data, expected_uncompressed_data)

    # Test to trigger lzma raising EOFError.
    with self.assertRaises(errors.BackEndError):
      decompressor.Decompress(b'This is a test.')

    # Test to trigger lzma raising IOError.
    decompressor = xz_decompressor.LZMADecompressor()

    with self.assertRaises(errors.BackEndError):
      decompressor.Decompress(b'This is a test.')


@unittest.skipIf(xz_decompressor is None, 'requires LZMA compression support')
class XZDecompressorTestCase(test_lib.DecompressorTestCase):
  """Tests for the xz decompressor object."""

  def testDecompress(self):
    """Tests the Decompress method."""
    decompressor = xz_decompressor.XZDecompressor()

    compressed_data = (
        b'\xfd7zXZ\x00\x00\x01i"\xde6\x02\xc0\x13\x0f!\x01\x16\x00\xc0\xb7\xdc'
        b'\xe9\x01\x00\x0eThis is a test.\x00\x00]\xc9\xc3\xc6\x00\x01#\x0f\xdb'
        b'\xdf\x90\x0e\x90B\x99\r\x01\x00\x00\x00\x00\x01YZ')

    uncompressed_data, _ = decompressor.Decompress(compressed_data)
    expected_uncompressed_data = b'This is a test.'
    self.assertEqual(uncompressed_data, expected_uncompressed_data)

    # Test to trigger xz raising EOFError.
    with self.assertRaises(errors.BackEndError):
      decompressor.Decompress(b'This is a test.')

    # Test to trigger xz raising IOError.
    decompressor = xz_decompressor.XZDecompressor()

    with self.assertRaises(errors.BackEndError):
      decompressor.Decompress(b'This is a test.')


if __name__ == '__main__':
  unittest.main()
