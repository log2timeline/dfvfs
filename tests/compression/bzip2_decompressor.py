#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the bzip2 decompressor object."""

import unittest

from dfvfs.compression import bzip2_decompressor
from dfvfs.lib import errors

from tests.compression import test_lib


class BZIP2DecompressorTestCase(test_lib.DecompressorTestCase):
  """Tests for the bzip2 decompressor object."""

  def testDecompress(self):
    """Tests the Decompress method."""
    decompressor = bzip2_decompressor.BZIP2Decompressor()

    compressed_data = (
        b'BZh91AY&SYa\x0e\xf5A\x00\x00\x02\x13\x80@\x01\x04\x00"`\x0c\x00 '
        b'\x00!\xa3M\x19\x082b\x18Q#\xa5\xc1"\xf1w$S\x85\t\x06\x10\xefT\x10')

    uncompressed_data, _ = decompressor.Decompress(compressed_data)
    expected_uncompressed_data = b'This is a test.'
    self.assertEqual(uncompressed_data, expected_uncompressed_data)

    # Test to trigger bz2 raising EOFError.
    with self.assertRaises(errors.BackEndError):
      decompressor.Decompress(b'This is a test.')

    # Test to trigger bz2 raising IOError.
    decompressor = bzip2_decompressor.BZIP2Decompressor()

    with self.assertRaises(errors.BackEndError):
      decompressor.Decompress(b'This is a test.')


if __name__ == '__main__':
  unittest.main()
