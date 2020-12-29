#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the base64 decoder object."""

import unittest

from dfvfs.encoding import base64_decoder
from dfvfs.lib import errors

from tests.encoding import test_lib


class Base64DecoderTestCase(test_lib.DecoderTestCase):
  """Tests for the base64 decoder object."""

  def testDecode(self):
    """Tests the Decode method."""
    decoder = base64_decoder.Base64Decoder()

    decoded_data, _ = decoder.Decode(b'AQIDBAUGBwg=')
    expected_decoded_data = b'\x01\x02\x03\x04\x05\x06\x07\x08'
    self.assertEqual(decoded_data, expected_decoded_data)

    decoder = base64_decoder.Base64Decoder()

    with self.assertRaises(errors.BackEndError):
      decoder.Decode(b'\x01\x02\x03\x04\x05\x06\x07\x08A')


if __name__ == '__main__':
  unittest.main()
