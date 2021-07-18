#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the attribute implementation using pytsk3."""

import unittest

from dfvfs.vfs import tsk_attribute

from tests import test_lib as shared_test_lib


class TSKAttributeTest(shared_test_lib.BaseTestCase):
  """Tests the TSK attribute."""

  def testTypeIndicator(self):
    """Tests the type_indicator property."""
    # TODO: improve test coverage.
    test_attribute = tsk_attribute.TSKAttribute(None)
    self.assertIsNotNone(test_attribute)
    self.assertIsNone(test_attribute.type_indicator)


if __name__ == '__main__':
  unittest.main()
