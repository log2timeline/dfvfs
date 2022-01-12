#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the VFS extent."""

import unittest

from dfvfs.vfs import extent

from tests import test_lib as shared_test_lib


class ExtentTest(shared_test_lib.BaseTestCase):
  """Tests the VFS extent."""

  def testInitialize(self):
    """Test the __init__ function."""
    test_extent = extent.Extent()
    self.assertIsNotNone(test_extent)


if __name__ == '__main__':
  unittest.main()
