#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the base16 decoder object."""

from __future__ import unicode_literals

import unittest

from dfvfs.encoding import base16_decoder
from dfvfs.lib import errors

from tests.encoding import test_lib


class Base16DecoderTestCase(test_lib.DecoderTestCase):
  """Tests for the base16 decoder object."""

  def testDecode(self):
    """Tests the Decode method."""
    decoder = base16_decoder.Base16Decoder()

    decoded_data, _ = decoder.Decode(b'0102030405060708')
    expected_decoded_data = b'\x01\x02\x03\x04\x05\x06\x07\x08'
    self.assertEqual(decoded_data, expected_decoded_data)

    decoder = base16_decoder.Base16Decoder()

    with self.assertRaises(errors.BackEndError):
      decoder.Decode(b'\x01\x02\x03\x04\x05\x06\x07\x08')


if __name__ == '__main__':
  unittest.main()
