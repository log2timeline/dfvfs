#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the decrypter interface."""

import unittest

from dfvfs.encryption import decrypter

from tests.encryption import test_lib


class DecrypterTestCase(test_lib.DecrypterTestCase):
  """Tests for the decrypter interface."""

  def testInitialize(self):
    """Tests the __init__ method."""
    test_decrypter = decrypter.Decrypter()
    self.assertIsNotNone(test_decrypter)

    with self.assertRaises(ValueError):
      decrypter.Decrypter(key=b'test1')


if __name__ == '__main__':
  unittest.main()
