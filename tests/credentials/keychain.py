#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the keychain object."""

from __future__ import unicode_literals

import unittest

from dfvfs.credentials import keychain
from dfvfs.lib import definitions
from dfvfs.path import factory

from tests import test_lib as shared_test_lib


class KeychainTest(shared_test_lib.BaseTestCase):
  """Class to test the keychain object."""

  def testCredentialGetSet(self):
    """Tests the GetCredential and SetCredential functions."""
    keychain_object = keychain.KeyChain()

    fake_path_spec = factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_FAKE, location='/test')
    bde_path_spec = factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_BDE, parent=fake_path_spec)

    with self.assertRaises(AttributeError):
      keychain_object.SetCredential(
          fake_path_spec, 'password', 'TEST')

    keychain_object.SetCredential(
        bde_path_spec, 'password', 'TEST')

    credential = keychain_object.GetCredential(
        fake_path_spec, 'password')
    self.assertIsNone(credential)

    credential = keychain_object.GetCredential(
        bde_path_spec, 'password')
    self.assertEqual(credential, 'TEST')

    credentials = keychain_object.GetCredentials(bde_path_spec)
    self.assertEqual(credentials, {'password': 'TEST'})


if __name__ == '__main__':
  unittest.main()
