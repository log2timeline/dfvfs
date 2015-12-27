#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the encoding manager."""

import unittest

from dfvfs.encoding import base16_decoder
from dfvfs.encoding import decoder
from dfvfs.encoding import manager
from dfvfs.lib import definitions


class TestDecoder(decoder.Decoder):
  """Class that implements a test decoder."""

  ENCODING_METHOD = u'test'

  def Decode(self, unused_encoded_data):
    """Decode the encoded data.

    Args:
      encoded_data: a byte string containing the encoded data.

    Returns:
      A tuple containing a byte string of the decoded data and
      the remaining encoded data.
    """
    return b'', b''


class EncodingManagerTest(unittest.TestCase):
  """Class to test the encoding manager."""

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

  def testGetDecoder(self):
    """Function to test the GetDecoder function."""
    decoder_object = manager.EncodingManager.GetDecoder(
        definitions.ENCODING_METHOD_BASE16)
    self.assertIsInstance(decoder_object, base16_decoder.Base16Decoder)

    decoder_object = manager.EncodingManager.GetDecoder(u'bogus')
    self.assertIsNone(decoder_object)


if __name__ == '__main__':
  unittest.main()
