#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Blowfish decrypter object."""

from __future__ import unicode_literals

import unittest

from dfvfs.encryption import blowfish_decrypter
from dfvfs.lib import definitions

from tests.encryption import test_lib


class BlowfishDecrypterTestCase(test_lib.DecrypterTestCase):
  """Tests for the Blowfish decrypter object."""

  _BLOWFISH_INITIALIZATION_VECTOR = b'This IV!'
  _BLOWFISH_KEY = b'This is a key123'

  def testInitialization(self):
    """Tests the initialization method."""
    # Test missing arguments.
    with self.assertRaises(ValueError):
      blowfish_decrypter.BlowfishDecrypter()

    # Test unsupported block cipher mode.
    with self.assertRaises(ValueError):
      blowfish_decrypter.BlowfishDecrypter(
          cipher_mode='bogus', key=self._BLOWFISH_KEY)

    # Test missing initialization vector.
    with self.assertRaises(ValueError):
      blowfish_decrypter.BlowfishDecrypter(
          cipher_mode=definitions.ENCRYPTION_MODE_CBC, key=self._BLOWFISH_KEY)

    # Test missing initialization vector with valid block cipher mode.
    blowfish_decrypter.BlowfishDecrypter(
        cipher_mode=definitions.ENCRYPTION_MODE_ECB, key=self._BLOWFISH_KEY)

    # Test incorrect key size.
    key = b'This is a key that is larger than the max key size of 448 bits.'
    with self.assertRaises(ValueError):
      blowfish_decrypter.BlowfishDecrypter(
          cipher_mode=definitions.ENCRYPTION_MODE_ECB, key=key)

    # Test incorrect initialization vector type.
    with self.assertRaises(TypeError):
      blowfish_decrypter.BlowfishDecrypter(
          cipher_mode=definitions.ENCRYPTION_MODE_CBC,
          initialization_vector='Wrong IV type', key=self._BLOWFISH_KEY)

    # Test incorrect initialization vector size.
    with self.assertRaises(ValueError):
      blowfish_decrypter.BlowfishDecrypter(
          cipher_mode=definitions.ENCRYPTION_MODE_CBC,
          initialization_vector=b'Wrong IV size', key=self._BLOWFISH_KEY)

  def testDecrypt(self):
    """Tests the Decrypt method."""
    decrypter = blowfish_decrypter.BlowfishDecrypter(
        cipher_mode=definitions.ENCRYPTION_MODE_CBC,
        initialization_vector=self._BLOWFISH_INITIALIZATION_VECTOR,
        key=self._BLOWFISH_KEY)

    # Test full decryption.
    expected_decrypted_data = b'This is secret encrypted text!!!'

    decrypted_data, remaining_encrypted_data = decrypter.Decrypt(
        b'}\x00\x99\xd2\xab\x1c\xcd\x80y\xef\x0b\x0f\xf72Rp\xbb\\h\x06\xff\x07'
        b'\x9a\xcfE\r\x8d\x18\x90\x8e\xfe\xa3', finalize=True)

    self.assertEqual(decrypted_data, expected_decrypted_data)
    self.assertEqual(remaining_encrypted_data, b'')

    # Reset decrypter.
    decrypter = blowfish_decrypter.BlowfishDecrypter(
        cipher_mode=definitions.ENCRYPTION_MODE_CBC,
        initialization_vector=self._BLOWFISH_INITIALIZATION_VECTOR,
        key=self._BLOWFISH_KEY)

    # Test partial decryption.
    partial_encrypted_data = b'}\x00\x99\xd2\xab\x1c\xcd\x80y\xef'

    decrypted_data, remaining_encrypted_data = decrypter.Decrypt(
        partial_encrypted_data)

    self.assertEqual(decrypted_data, b'')
    self.assertEqual(remaining_encrypted_data, partial_encrypted_data)


if __name__ == '__main__':
  unittest.main()
