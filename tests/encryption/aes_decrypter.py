#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the AES decrypter object."""

from __future__ import unicode_literals

import unittest

from dfvfs.encryption import aes_decrypter
from dfvfs.lib import definitions

from tests.encryption import test_lib


class AESDecrypterTestCase(test_lib.DecrypterTestCase):
  """Tests for the AES decrypter object."""

  _AES_INITIALIZATION_VECTOR = b'This is an IV456'
  _AES_KEY = b'This is a key123'

  def testInitialization(self):
    """Tests the initialization method."""
    # Test missing arguments.
    with self.assertRaises(ValueError):
      aes_decrypter.AESDecrypter()

    # Test unsupported block cipher mode.
    with self.assertRaises(ValueError):
      aes_decrypter.AESDecrypter(
          cipher_mode='bogus', key=self._AES_KEY)

    # Test missing initialization vector.
    with self.assertRaises(ValueError):
      aes_decrypter.AESDecrypter(
          cipher_mode=definitions.ENCRYPTION_MODE_CBC, key=self._AES_KEY)

    # Test missing initialization vector with valid block cipher mode.
    aes_decrypter.AESDecrypter(
        cipher_mode=definitions.ENCRYPTION_MODE_ECB, key=self._AES_KEY)

    # Test incorrect key size.
    with self.assertRaises(ValueError):
      aes_decrypter.AESDecrypter(
          cipher_mode=definitions.ENCRYPTION_MODE_ECB, key=b'Wrong key size')

    # Test incorrect initialization vector type.
    with self.assertRaises(TypeError):
      aes_decrypter.AESDecrypter(
          cipher_mode=definitions.ENCRYPTION_MODE_CBC,
          initialization_vector='Wrong IV type', key=self._AES_KEY)

    # Test incorrect initialization vector size.
    with self.assertRaises(ValueError):
      aes_decrypter.AESDecrypter(
          cipher_mode=definitions.ENCRYPTION_MODE_CBC,
          initialization_vector=b'Wrong IV size', key=self._AES_KEY)

  def testDecrypt(self):
    """Tests the Decrypt method."""
    decrypter = aes_decrypter.AESDecrypter(
        cipher_mode=definitions.ENCRYPTION_MODE_CBC,
        initialization_vector=self._AES_INITIALIZATION_VECTOR,
        key=self._AES_KEY)

    # Test full decryption.
    expected_decrypted_data = b'This is secret encrypted text!!!'

    decrypted_data, remaining_encrypted_data = decrypter.Decrypt(
        b'2|\x7f\xd7\xff\xbay\xf9\x95?\x81\xc7\xaafV\xceB\x01\xdb8E7\xfe'
        b'\x92j\xf0\x1d(\xb9\x9f\xad\x13', finalize=True)

    self.assertEqual(decrypted_data, expected_decrypted_data)
    self.assertEqual(remaining_encrypted_data, b'')

    # Reset decrypter.
    decrypter = aes_decrypter.AESDecrypter(
        cipher_mode=definitions.ENCRYPTION_MODE_CBC,
        initialization_vector=self._AES_INITIALIZATION_VECTOR,
        key=self._AES_KEY)

    # Test partial decryption.
    partial_encrypted_data = (
        b'2|\x7f\xd7\xff\xbay\xf9\x95?\x81\xc7\xaafV\xceB\x01\xdb8E7\xfe')

    decrypted_data, remaining_encrypted_data = decrypter.Decrypt(
        partial_encrypted_data)
    self.assertEqual(decrypted_data, b'')
    self.assertEqual(remaining_encrypted_data, partial_encrypted_data)


if __name__ == '__main__':
  unittest.main()
