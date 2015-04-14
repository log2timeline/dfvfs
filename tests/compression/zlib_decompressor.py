#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the zlib decompressor object."""

import unittest

from dfvfs.compression import zlib_decompressor
from tests.compression import test_lib
from dfvfs.lib import errors


class ZlibDecompressorTestCase(test_lib.DecompressorTestCase):
  """Tests for the zlib decompressor object."""

  def testDecompress(self):
    """Tests the Decompress method."""
    decompressor = zlib_decompressor.ZlibDecompressor()

    compressed_data = (
        b'x\x9c\x0b\xc9\xc8,V\x00\xa2D\x85\x92\xd4\xe2\x12=\x00)\x97\x05$')

    uncompressed_data, _ = decompressor.Decompress(compressed_data)
    expected_uncompressed_data = b'This is a test.'
    self.assertEquals(uncompressed_data, expected_uncompressed_data)

    decompressor = zlib_decompressor.ZlibDecompressor()

    with self.assertRaises(errors.BackEndError):
      _, _ = decompressor.Decompress(b'This is a test.')


class DeflateDecompressorTestCase(test_lib.DecompressorTestCase):
  """Tests for the zlib decompressor object."""

  def testDecompress(self):
    """Tests the Decompress method."""
    decompressor = zlib_decompressor.DeflateDecompressor()

    compressed_data = (
        b'\x0b\xc9\xc8,V\x00\xa2D\x85\x92\xd4\xe2\x12=\x00)\x97\x05$')

    uncompressed_data, _ = decompressor.Decompress(compressed_data)
    expected_uncompressed_data = b'This is a test.'
    self.assertEquals(uncompressed_data, expected_uncompressed_data)

    decompressor = zlib_decompressor.DeflateDecompressor()

    with self.assertRaises(errors.BackEndError):
      _, _ = decompressor.Decompress(b'This is a test.')


if __name__ == '__main__':
  unittest.main()
