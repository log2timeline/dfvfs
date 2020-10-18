#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the encryption manager."""

from __future__ import unicode_literals

import unittest

from dfvfs.encryption import decrypter
from dfvfs.encryption import manager
from dfvfs.encryption import rc4_decrypter
from dfvfs.lib import definitions

from tests import test_lib as shared_test_lib


class TestDecrypter(decrypter.Decrypter):
  """Test decrypter."""

  ENCRYPTION_METHOD = 'test'

  # pylint: disable=unused-argument
  def Decrypt(self, encrypted_data, finalize=False):
    """Decrypt the encrypted data.

    Args:
      encrypted_data (bytes): the encrypted data.
      finalize (Optional[bool]): True if the end of data has been reached and
          the cipher context should be finalized.

    Returns:
      tuple[bytes, bytes]: byte string of the decrypted data and the remaining
          encrypted data.
    """
    return b'', b''


class EncryptionManagerTest(shared_test_lib.BaseTestCase):
  """Encryption manager tests."""

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

    with self.assertRaises(KeyError):
      manager.EncryptionManager.DeregisterDecrypter(TestDecrypter)

  def testGetDecrypter(self):
    """Function to test the GetDecrypter function."""
    decrypter_object = manager.EncryptionManager.GetDecrypter(
        definitions.ENCRYPTION_METHOD_RC4, key=b'test1')
    self.assertIsInstance(decrypter_object, rc4_decrypter.RC4Decrypter)

    decrypter_object = manager.EncryptionManager.GetDecrypter('bogus')
    self.assertIsNone(decrypter_object)


if __name__ == '__main__':
  unittest.main()
