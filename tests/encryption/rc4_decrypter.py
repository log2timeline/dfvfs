#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the RC4 decrypter object."""

import unittest

from dfvfs.encryption import rc4_decrypter
from dfvfs.lib import errors

from tests.encryption import test_lib


class RC4DecrypterTestCase(test_lib.DecrypterTestCase):
  """Tests for the RC4 decrypter object."""

  def testInitialize(self):
    """Tests the __init__ method."""
    try:
      decrypter = rc4_decrypter.RC4Decrypter(key=b'test1')
    except errors.BackEndError:
      raise unittest.SkipTest('missing cryptograpy RC4 support')

    self.assertIsNotNone(decrypter)

    with self.assertRaises(ValueError):
      rc4_decrypter.RC4Decrypter()

  def testDecrypt(self):
    """Tests the Decrypt method."""
    try:
      decrypter = rc4_decrypter.RC4Decrypter(key=b'test1')
    except errors.BackEndError:
      raise unittest.SkipTest('missing cryptograpy RC4 support')

    decrypted_data, _ = decrypter.Decrypt(b'\xef6\xcd\x14\xfe\xf5+y')
    expected_decrypted_data = b'\x01\x02\x03\x04\x05\x06\x07\x08'
    self.assertEqual(decrypted_data, expected_decrypted_data)


if __name__ == '__main__':
  unittest.main()
