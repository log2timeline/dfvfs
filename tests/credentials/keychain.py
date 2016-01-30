#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the keychain object."""

import unittest

from dfvfs.credentials import keychain
from dfvfs.lib import definitions
from dfvfs.path import factory


class KeychainTest(unittest.TestCase):
  """Class to test the keychain object."""

  def testCredentialGetSet(self):
    """Tests the GetCredential and SetCredential functions."""
    keychain_object = keychain.KeyChain()

    fake_path_spec = factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_FAKE, location=u'/test')
    bde_path_spec = factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_BDE, parent=fake_path_spec)

    with self.assertRaises(AttributeError):
      keychain_object.SetCredential(
          fake_path_spec, u'password', u'TEST')

    keychain_object.SetCredential(
        bde_path_spec, u'password', u'TEST')

    credential = keychain_object.GetCredential(
        fake_path_spec, u'password')
    self.assertIsNone(credential)

    credential = keychain_object.GetCredential(
        bde_path_spec, u'password')
    self.assertEqual(credential, u'TEST')

    credentials = keychain_object.GetCredentials(bde_path_spec)
    self.assertEqual(credentials, {u'password': u'TEST'})


if __name__ == '__main__':
  unittest.main()
