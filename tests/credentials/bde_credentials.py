#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the BitLocker Drive Encryption (BDE) credentials."""

from __future__ import unicode_literals

import unittest

from dfvfs.credentials import bde_credentials

from tests import test_lib as shared_test_lib


class BDECredentials(shared_test_lib.BaseTestCase):
  """Tests the BitLocker Drive Encryption (BDE) credentials."""

  def testInitialize(self):
    """Tests the __init__ function."""
    test_credentials = bde_credentials.BDECredentials()
    self.assertIsNotNone(test_credentials)


if __name__ == '__main__':
  unittest.main()
