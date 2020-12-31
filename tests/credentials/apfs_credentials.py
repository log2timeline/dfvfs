#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Apple File System (APFS) credentials."""

import unittest

from dfvfs.credentials import apfs_credentials

from tests import test_lib as shared_test_lib


class APFSCredentials(shared_test_lib.BaseTestCase):
  """Tests the Apple File System (APFS) credentials."""

  def testInitialize(self):
    """Tests the __init__ function."""
    test_credentials = apfs_credentials.APFSCredentials()
    self.assertIsNotNone(test_credentials)


if __name__ == '__main__':
  unittest.main()
