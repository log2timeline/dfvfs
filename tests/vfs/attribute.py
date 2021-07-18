#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the VFS attribute interface."""

import unittest

from dfvfs.vfs import attribute

from tests import test_lib as shared_test_lib


class AttributeTest(shared_test_lib.BaseTestCase):
  """Tests the VFS attribute interface."""

  def testTypeIndicator(self):
    """Tests the type_indicator property."""
    test_attribute = attribute.Attribute()
    self.assertIsNotNone(test_attribute)
    self.assertIsNone(test_attribute.type_indicator)


if __name__ == '__main__':
  unittest.main()
