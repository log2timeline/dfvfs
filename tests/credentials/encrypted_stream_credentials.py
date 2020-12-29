#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the encrypted stream credentials."""

import unittest

from dfvfs.credentials import encrypted_stream_credentials

from tests import test_lib as shared_test_lib


class APFSCredentials(shared_test_lib.BaseTestCase):
  """Tests the encrypted stream credentials."""

  def testInitialize(self):
    """Tests the __init__ function."""
    test_credentials = encrypted_stream_credentials.EncryptedStreamCredentials()
    self.assertIsNotNone(test_credentials)


if __name__ == '__main__':
  unittest.main()
