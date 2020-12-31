#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the encrypted stream path specification implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import encrypted_stream_path_spec

from tests.path import test_lib


class EncryptedStreamPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the encrypted stream path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = encrypted_stream_path_spec.EncryptedStreamPathSpec(
        encryption_method='test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      encrypted_stream_path_spec.EncryptedStreamPathSpec(
          encryption_method='test', parent=None)

    with self.assertRaises(ValueError):
      encrypted_stream_path_spec.EncryptedStreamPathSpec(
          encryption_method=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      encrypted_stream_path_spec.EncryptedStreamPathSpec(
          encryption_method='test', parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = encrypted_stream_path_spec.EncryptedStreamPathSpec(
        encryption_method='test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: ENCRYPTED_STREAM, encryption_method: test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    # Test with credentials.
    path_spec = encrypted_stream_path_spec.EncryptedStreamPathSpec(
        cipher_mode=definitions.ENCRYPTION_MODE_CBC, encryption_method='test',
        initialization_vector=b'\x54\x68\x69\x73\x20\x69\x73\x20\x49\x56\x2e',
        key=b'\x54\x68\x69\x73\x20\x69\x73\x20\x6b\x65\x79\x2e',
        parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        ('type: ENCRYPTED_STREAM, cipher_mode: cbc, encryption_method: test, '
         'initialization_vector: 546869732069732049562e, '
         'key: 54686973206973206b65792e'),
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
