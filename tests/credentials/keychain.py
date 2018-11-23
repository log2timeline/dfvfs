#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the key chain."""

from __future__ import unicode_literals

import unittest

from dfvfs.credentials import keychain
from dfvfs.lib import definitions
from dfvfs.path import factory

from tests import test_lib as shared_test_lib


class KeychainTest(shared_test_lib.BaseTestCase):
  """Tests the key chain."""

  # TODO: add tests for Empty
  # TODO: add tests for ExtractCredentialsFromPathSpec

  def testCredentialGetSet(self):
    """Tests the GetCredential and SetCredential functions."""
    test_keychain = keychain.KeyChain()

    fake_path_spec = factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_FAKE, location='/test')
    bde_path_spec = factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_BDE, parent=fake_path_spec)

    with self.assertRaises(AttributeError):
      test_keychain.SetCredential(fake_path_spec, 'password', 'TEST')

    test_keychain.SetCredential(bde_path_spec, 'password', 'TEST')

    credential = test_keychain.GetCredential(fake_path_spec, 'password')
    self.assertIsNone(credential)

    credential = test_keychain.GetCredential(bde_path_spec, 'password')
    self.assertEqual(credential, 'TEST')

    credentials = test_keychain.GetCredentials(bde_path_spec)
    self.assertEqual(credentials, {'password': 'TEST'})


if __name__ == '__main__':
  unittest.main()
