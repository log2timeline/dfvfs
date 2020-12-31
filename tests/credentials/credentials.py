#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the credentials interface."""

import unittest

from dfvfs.credentials import credentials

from tests import test_lib as shared_test_lib


class Credentials(shared_test_lib.BaseTestCase):
  """Tests the credentials interface."""

  def testInitialize(self):
    """Tests the __init__ function."""
    with self.assertRaises(ValueError):
      credentials.Credentials()


if __name__ == '__main__':
  unittest.main()
