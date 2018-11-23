#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the FileVault Drive Encryption (FVDE) credentials."""

from __future__ import unicode_literals

import unittest

from dfvfs.credentials import fvde_credentials

from tests import test_lib as shared_test_lib


class FVDECredentials(shared_test_lib.BaseTestCase):
  """Tests the FileVault Drive Encryption (FVDE) credentials."""

  def testInitialize(self):
    """Tests the __init__ function."""
    test_credentials = fvde_credentials.FVDECredentials()
    self.assertIsNotNone(test_credentials)


if __name__ == '__main__':
  unittest.main()
