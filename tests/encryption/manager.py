#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the encryption manager."""

import unittest

from dfvfs.encryption import decrypter
from dfvfs.encryption import manager
from dfvfs.encryption import rc4_decrypter
from dfvfs.lib import definitions


class TestDecrypter(decrypter.Decrypter):
  """Class that implements a test decrypter."""

  ENCRYPTION_METHOD = u'test'

  def Decrypt(self, unused_encrypted_data):
    """Decrypt the encrypted data.

    Args:
      encrypted_data: a byte string containing the encrypted data.

    Returns:
      A tuple containing a byte string of the decrypted data and
      the remaining encrypted data.
    """
    return b'', b''


class EncryptionManagerTest(unittest.TestCase):
  """Class to test the encryption manager."""

  def testDecrypterRegistration(self):
    """Tests the DeregisterDecrypter and DeregisterDecrypter functions."""
    # pylint: disable=protected-access
    number_of_decrypters = len(manager.EncryptionManager._decrypters)

    manager.EncryptionManager.RegisterDecrypter(TestDecrypter)
    self.assertEqual(
        len(manager.EncryptionManager._decrypters),
        number_of_decrypters + 1)

    with self.assertRaises(KeyError):
      manager.EncryptionManager.RegisterDecrypter(TestDecrypter)

    manager.EncryptionManager.DeregisterDecrypter(TestDecrypter)
    self.assertEqual(
        len(manager.EncryptionManager._decrypters), number_of_decrypters)

  def testGetDecrypter(self):
    """Function to test the GetDecrypter function."""
    decrypter_object = manager.EncryptionManager.GetDecrypter(
        definitions.ENCRYPTION_METHOD_RC4, key=b'test')
    self.assertIsInstance(decrypter_object, rc4_decrypter.RC4Decrypter)

    decrypter_object = manager.EncryptionManager.GetDecrypter(u'bogus')
    self.assertIsNone(decrypter_object)


if __name__ == '__main__':
  unittest.main()
