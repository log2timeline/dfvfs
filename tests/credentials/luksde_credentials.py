#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the LUKS Drive Encryption credentials."""

import unittest

from dfvfs.credentials import luksde_credentials

from tests import test_lib as shared_test_lib


class LUKSDECredentials(shared_test_lib.BaseTestCase):
  """Tests the LUKS Drive Encryption credentials."""

  def testInitialize(self):
    """Tests the __init__ function."""
    test_credentials = luksde_credentials.LUKSDECredentials()
    self.assertIsNotNone(test_credentials)


if __name__ == '__main__':
  unittest.main()
