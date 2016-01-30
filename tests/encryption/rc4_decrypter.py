#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the RC4 decrypter object."""

import unittest

from dfvfs.encryption import rc4_decrypter
from tests.encryption import test_lib


class RC4DecrypterTestCase(test_lib.DecrypterTestCase):
  """Tests for the RC4 decrypter object."""

  def testDecrypt(self):
    """Tests the Decrypt method."""
    decrypter = rc4_decrypter.RC4Decrypter(key=b'test')

    decrypted_data, _ = decrypter.Decrypt(b'\xaf\x8d\x24\x15\xe5\x2c\x7a\x2d')
    expected_decrypted_data = b'\x01\x02\x03\x04\x05\x06\x07\x08'
    self.assertEqual(decrypted_data, expected_decrypted_data)


if __name__ == '__main__':
  unittest.main()
