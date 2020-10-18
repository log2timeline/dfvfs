#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the credentials manager."""

from __future__ import unicode_literals

import unittest

from dfvfs.credentials import apfs_credentials
from dfvfs.credentials import credentials
from dfvfs.credentials import manager
from dfvfs.path import apfs_container_path_spec
from dfvfs.path import fake_path_spec

from tests import test_lib as shared_test_lib


class TestCredentials(credentials.Credentials):
  """Credentials for testing."""

  CREDENTIALS = frozenset(['password'])

  TYPE_INDICATOR = 'test'


class CredentialsManagerTest(shared_test_lib.BaseTestCase):
  """Credentials manager tests."""

  def testCredentialsRegistration(self):
    """Tests the DeregisterCredentials and DeregisterCredentials functions."""
    # pylint: disable=protected-access
    test_credentials = TestCredentials()

    number_of_credentials = len(manager.CredentialsManager._credentials)

    manager.CredentialsManager.RegisterCredentials(test_credentials)
    self.assertEqual(
        len(manager.CredentialsManager._credentials), number_of_credentials + 1)

    with self.assertRaises(KeyError):
      manager.CredentialsManager.RegisterCredentials(test_credentials)

    manager.CredentialsManager.DeregisterCredentials(test_credentials)
    self.assertEqual(
        len(manager.CredentialsManager._credentials), number_of_credentials)

    with self.assertRaises(KeyError):
      manager.CredentialsManager.DeregisterCredentials(test_credentials)

  def testGetCredentials(self):
    """Function to test the GetCredentials function."""
    test_path_spec = fake_path_spec.FakePathSpec(location='/fake')
    test_path_spec = apfs_container_path_spec.APFSContainerPathSpec(
        location='/', parent=fake_path_spec)

    credentials_object = manager.CredentialsManager.GetCredentials(
        test_path_spec)
    self.assertIsInstance(credentials_object, apfs_credentials.APFSCredentials)

    test_path_spec = fake_path_spec.FakePathSpec(location='/fake')
    credentials_object = manager.CredentialsManager.GetCredentials(
        test_path_spec)
    self.assertIsNone(credentials_object)


if __name__ == '__main__':
  unittest.main()
