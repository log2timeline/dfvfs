#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the RC4 decrypter object."""

from __future__ import unicode_literals

import unittest

from cryptography.hazmat.primitives.ciphers import algorithms

from dfvfs.encryption import decrypter
from dfvfs.lib import definitions

from tests.encryption import test_lib


class DecrypterTestCase(test_lib.DecrypterTestCase):
  """Tests for the decrypter interface."""

  def testInitialize(self):
    """Tests the __init__ method."""
    test_decrypter = decrypter.Decrypter()
    self.assertIsNotNone(test_decrypter)

    with self.assertRaises(ValueError):
      decrypter.Decrypter(key=b'test1')


class CryptographyBlockCipherDecrypterTest(test_lib.DecrypterTestCase):
  """Tests for the block cipher decrypter using Cryptography."""

  _DES3_INITIALIZATION_VECTOR = b'This IV!'
  _DES3_KEY = b'This is a key123'

  def testInitialize(self):
    """Tests the __init__ method."""
    algorithm = algorithms.TripleDES(self._DES3_KEY)

    test_decrypter = decrypter.CryptographyBlockCipherDecrypter(
        algorithm=algorithm, cipher_mode=definitions.ENCRYPTION_MODE_CBC,
        initialization_vector=self._DES3_INITIALIZATION_VECTOR)
    self.assertIsNotNone(test_decrypter)

    test_decrypter = decrypter.CryptographyBlockCipherDecrypter(
        algorithm=algorithm, cipher_mode=definitions.ENCRYPTION_MODE_CFB,
        initialization_vector=self._DES3_INITIALIZATION_VECTOR)
    self.assertIsNotNone(test_decrypter)

    test_decrypter = decrypter.CryptographyBlockCipherDecrypter(
        algorithm=algorithm, cipher_mode=definitions.ENCRYPTION_MODE_ECB)
    self.assertIsNotNone(test_decrypter)

    test_decrypter = decrypter.CryptographyBlockCipherDecrypter(
        algorithm=algorithm, cipher_mode=definitions.ENCRYPTION_MODE_OFB,
        initialization_vector=self._DES3_INITIALIZATION_VECTOR)
    self.assertIsNotNone(test_decrypter)

    with self.assertRaises(ValueError):
      decrypter.CryptographyBlockCipherDecrypter(
          algorithm=algorithm, cipher_mode=definitions.ENCRYPTION_MODE_CBC)


if __name__ == '__main__':
  unittest.main()
