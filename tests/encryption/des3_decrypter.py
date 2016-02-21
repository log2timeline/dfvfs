#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the triple DES decrypter object."""

import unittest

from dfvfs.encryption import des3_decrypter
from dfvfs.lib import definitions
from tests.encryption import test_lib


class DES3DecrypterTestCase(test_lib.DecrypterTestCase):
  """Tests for the triple DES decrypter object."""

  def testDecrypt(self):
    """Tests the Decrypt method."""
    decrypter = des3_decrypter.DES3Decrypter(
        key=u'This is a key123',
        mode=definitions.ENCRYPTION_MODE_CBC,
        initialization_vector=u'This IV!')

    # Test full decryption.
    decrypted_data, _ = decrypter.Decrypt(
        b'e\x86k\t\x01W\xd7d\xe4\xa4\xb3~\x80\xd3\xc3\x7fq{E}:L\n '
        b'.2\xd1\xcf\x8a\xf1\xa0!')
    expected_decrypted_data = b'This is secret encrypted text!!!'
    self.assertEqual(expected_decrypted_data, decrypted_data)

    # Reset decrypter.
    decrypter = des3_decrypter.DES3Decrypter(
        key=u'This is a key123',
        mode=definitions.ENCRYPTION_MODE_CBC,
        initialization_vector=u'This IV!')

    # Test partial decryption.
    decrypted_data, encrypted_data = decrypter.Decrypt(
        b'e\x86k\t\x01W\xd7d\xe4\xa4\xb3~\x80')
    expected_decrypted_data = b'This is '
    expected_encrypted_data = b'\xe4\xa4\xb3~\x80'
    self.assertEqual(expected_decrypted_data, decrypted_data)
    self.assertEqual(expected_encrypted_data, encrypted_data)

    decrypted_data, encrypted_data = decrypter.Decrypt(
        b'\xe4\xa4\xb3~\x80\xd3\xc3\x7fq{E}:L\n '
        b'.2\xd1\xcf\x8a\xf1\xa0!')
    expected_decrypted_data = b'secret encrypted text!!!'
    expected_encrypted_data = b''
    self.assertEqual(expected_decrypted_data, decrypted_data)
    self.assertEqual(expected_encrypted_data, encrypted_data)


if __name__ == '__main__':
  unittest.main()
