#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the encoding manager."""

import unittest

from dfvfs.encoding import base16_decoder
from dfvfs.encoding import decoder
from dfvfs.encoding import manager
from dfvfs.lib import definitions

from tests import test_lib as shared_test_lib


class TestDecoder(decoder.Decoder):
  """Class that implements a test decoder."""

  ENCODING_METHOD = 'test'

  def Decode(self, encoded_data):
    """Decode the encoded data.

    Args:
      encoded_data (byte): encoded data.

    Returns:
      tuple(bytes, bytes): decoded data and remaining encoded data.
    """
    return b'', b''


class EncodingManagerTest(shared_test_lib.BaseTestCase):
  """Encoding manager tests."""

  def testDecoderRegistration(self):
    """Tests the DeregisterDecoder and DeregisterDecoder functions."""
    # pylint: disable=protected-access
    number_of_decoders = len(manager.EncodingManager._decoders)

    manager.EncodingManager.RegisterDecoder(TestDecoder)
    self.assertEqual(
        len(manager.EncodingManager._decoders),
        number_of_decoders + 1)

    with self.assertRaises(KeyError):
      manager.EncodingManager.RegisterDecoder(TestDecoder)

    manager.EncodingManager.DeregisterDecoder(TestDecoder)
    self.assertEqual(
        len(manager.EncodingManager._decoders), number_of_decoders)

    with self.assertRaises(KeyError):
      manager.EncodingManager.DeregisterDecoder(TestDecoder)

  def testGetDecoder(self):
    """Function to test the GetDecoder function."""
    decoder_object = manager.EncodingManager.GetDecoder(
        definitions.ENCODING_METHOD_BASE16)
    self.assertIsInstance(decoder_object, base16_decoder.Base16Decoder)

    decoder_object = manager.EncodingManager.GetDecoder('bogus')
    self.assertIsNone(decoder_object)


if __name__ == '__main__':
  unittest.main()
