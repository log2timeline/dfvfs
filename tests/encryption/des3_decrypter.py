#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the triple DES decrypter object."""

import unittest

from dfvfs.encryption import des3_decrypter
from dfvfs.lib import definitions
from dfvfs.lib import errors

from tests.encryption import test_lib


class DES3DecrypterTestCase(test_lib.DecrypterTestCase):
  """Tests for the triple DES decrypter object."""

  _DES3_INITIALIZATION_VECTOR = b'This IV!'
  _DES3_KEY = b'This is a key123'

  def testInitialization(self):
    """Tests the initialization method."""
    # Test missing initialization vector with valid block cipher mode.
    try:
      des3_decrypter.DES3Decrypter(
          cipher_mode=definitions.ENCRYPTION_MODE_ECB, key=self._DES3_KEY)
    except errors.BackEndError:
      raise unittest.SkipTest('missing cryptograpy triple DES support')

    # Test missing arguments.
    with self.assertRaises(ValueError):
      des3_decrypter.DES3Decrypter()

    # Test unsupported block cipher mode.
    with self.assertRaises(ValueError):
      des3_decrypter.DES3Decrypter(
          cipher_mode='bogus', key=self._DES3_KEY)

    # Test missing initialization vector.
    with self.assertRaises(ValueError):
      des3_decrypter.DES3Decrypter(
          cipher_mode=definitions.ENCRYPTION_MODE_CBC, key=self._DES3_KEY)

    # Test incorrect key size.
    with self.assertRaises(ValueError):
      des3_decrypter.DES3Decrypter(
          cipher_mode=definitions.ENCRYPTION_MODE_ECB, key=b'Wrong key size')

    # Test incorrect initialization vector type.
    with self.assertRaises(TypeError):
      des3_decrypter.DES3Decrypter(
          cipher_mode=definitions.ENCRYPTION_MODE_CBC,
          initialization_vector='Wrong IV type', key=self._DES3_KEY)

    # Test incorrect initialization vector size.
    with self.assertRaises(ValueError):
      des3_decrypter.DES3Decrypter(
          cipher_mode=definitions.ENCRYPTION_MODE_CBC,
          initialization_vector=b'Wrong IV size', key=self._DES3_KEY)

  def testDecrypt(self):
    """Tests the Decrypt method."""
    try:
      decrypter = des3_decrypter.DES3Decrypter(
          cipher_mode=definitions.ENCRYPTION_MODE_CBC,
          initialization_vector=self._DES3_INITIALIZATION_VECTOR,
          key=self._DES3_KEY)
    except errors.BackEndError:
      raise unittest.SkipTest('missing cryptograpy triple DES support')

    # Test full decryption.
    expected_decrypted_data = b'This is secret encrypted text!!!'

    decrypted_data, remaining_encrypted_data = decrypter.Decrypt(
        b'e\x86k\t\x01W\xd7d\xe4\xa4\xb3~\x80\xd3\xc3\x7fq{E}:L\n '
        b'.2\xd1\xcf\x8a\xf1\xa0!', finalize=True)

    self.assertEqual(decrypted_data, expected_decrypted_data)
    self.assertEqual(remaining_encrypted_data, b'')

    # Reset decrypter.
    try:
      decrypter = des3_decrypter.DES3Decrypter(
          cipher_mode=definitions.ENCRYPTION_MODE_CBC,
          initialization_vector=self._DES3_INITIALIZATION_VECTOR,
          key=self._DES3_KEY)
    except errors.BackEndError:
      raise unittest.SkipTest('missing cryptograpy triple DES support')

    # Test partial decryption.
    partial_encrypted_data = b'e\x86k\t\x01W\xd7d\xe4\xa4\xb3~\x80'

    decrypted_data, remaining_encrypted_data = decrypter.Decrypt(
        partial_encrypted_data)
    self.assertEqual(decrypted_data, b'')
    self.assertEqual(remaining_encrypted_data, partial_encrypted_data)


if __name__ == '__main__':
  unittest.main()
