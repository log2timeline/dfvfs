#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Core Storage (CS) credentials."""

import unittest

from dfvfs.credentials import cs_credentials

from tests import test_lib as shared_test_lib


class CSCredentials(shared_test_lib.BaseTestCase):
  """Tests the Core Storage (CS) credentials."""

  def testInitialize(self):
    """Tests the __init__ function."""
    test_credentials = cs_credentials.CSCredentials()
    self.assertIsNotNone(test_credentials)


if __name__ == '__main__':
  unittest.main()
