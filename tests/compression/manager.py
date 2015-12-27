#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the compression manager."""

import unittest

from dfvfs.compression import decompressor
from dfvfs.compression import manager
from dfvfs.compression import zlib_decompressor
from dfvfs.lib import definitions


class TestDecompressor(decompressor.Decompressor):
  """Class that implements a test decompressor."""

  COMPRESSION_METHOD = u'test'

  def Decompress(self, unused_compressed_data):
    """Decompresses the compressed data.

    Args:
      compressed_data: a byte string containing the compressed data.

    Returns:
      A tuple containing a byte string of the uncompressed data and
      the remaining compressed data.
    """
    return b'', b''


class CompressionManagerTest(unittest.TestCase):
  """Class to test the compression manager."""

  def testDecompressorRegistration(self):
    """Tests the DeregisterDecompressor and DeregisterDecompressor functions."""
    # pylint: disable=protected-access
    number_of_decompressors = len(manager.CompressionManager._decompressors)

    manager.CompressionManager.RegisterDecompressor(TestDecompressor)
    self.assertEqual(
        len(manager.CompressionManager._decompressors),
        number_of_decompressors + 1)

    with self.assertRaises(KeyError):
      manager.CompressionManager.RegisterDecompressor(TestDecompressor)

    manager.CompressionManager.DeregisterDecompressor(TestDecompressor)
    self.assertEqual(
        len(manager.CompressionManager._decompressors), number_of_decompressors)

  def testGetDecompressor(self):
    """Function to test the GetDecompressor function."""
    decompressor_object = manager.CompressionManager.GetDecompressor(
        definitions.COMPRESSION_METHOD_ZLIB)
    self.assertIsInstance(
        decompressor_object, zlib_decompressor.ZlibDecompressor)

    decompressor_object = manager.CompressionManager.GetDecompressor(u'bogus')
    self.assertIsNone(decompressor_object)


if __name__ == '__main__':
  unittest.main()
