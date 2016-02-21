#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Blowfish decrypter object."""

import unittest

from dfvfs.encryption import blowfish_decrypter
from dfvfs.lib import definitions
from tests.encryption import test_lib


class BlowfishDecrypterTestCase(test_lib.DecrypterTestCase):
  """Tests for the Blowfish decrypter object."""

  def testDecrypt(self):
    """Tests the Decrypt method."""
    decrypter = blowfish_decrypter.BlowfishDecrypter(
        key=u'This is a key123',
        mode=definitions.ENCRYPTION_MODE_CBC,
        initialization_vector=u'This IV!')

    # Test full decryption.
    decrypted_data, _ = decrypter.Decrypt(
        b'}\x00\x99\xd2\xab\x1c\xcd\x80y\xef\x0b\x0f\xf72Rp\xbb\\h\x06\xff\x07'
        b'\x9a\xcfE\r\x8d\x18\x90\x8e\xfe\xa3')
    expected_decrypted_data = b'This is secret encrypted text!!!'
    self.assertEqual(expected_decrypted_data, decrypted_data)

    # Reset decrypter.
    decrypter = blowfish_decrypter.BlowfishDecrypter(
        key=u'This is a key123',
        mode=definitions.ENCRYPTION_MODE_CBC,
        initialization_vector=u'This IV!')

    # Test partial decryption.
    decrypted_data, encrypted_data = decrypter.Decrypt(
        b'}\x00\x99\xd2\xab\x1c\xcd\x80y\xef')
    expected_decrypted_data = b'This is '
    expected_encrypted_data = b'y\xef'
    self.assertEqual(expected_decrypted_data, decrypted_data)
    self.assertEqual(expected_encrypted_data, encrypted_data)

    decrypted_data, encrypted_data = decrypter.Decrypt(
        b'y\xef\x0b\x0f\xf72Rp\xbb\\h\x06\xff\x07\x9a\xcfE\r\x8d\x18\x90\x8e'
        b'\xfe\xa3')
    expected_decrypted_data = b'secret encrypted text!!!'
    expected_encrypted_data = b''
    self.assertEqual(expected_decrypted_data, decrypted_data)
    self.assertEqual(expected_encrypted_data, encrypted_data)


if __name__ == '__main__':
  unittest.main()
