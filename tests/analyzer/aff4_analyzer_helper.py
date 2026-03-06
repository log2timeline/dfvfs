#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the AFF4 analyzer helper implementation."""

import unittest

from dfvfs.analyzer import aff4_analyzer_helper
from dfvfs.lib import definitions

from tests import test_lib


class AFF4AnalyzerHelperTest(test_lib.BaseTestCase):
  """Tests for the AFF4 analyzer helper implementation."""

  def testAnalyzeFileObject(self):
    """Tests AnalyzeFileObject."""
    analyzer_helper = aff4_analyzer_helper.AFF4AnalyzerHelper()

    test_file = self._GetTestFilePath(['aff4', 'Base-Linear.aff4'])
    self._SkipIfPathNotExists(test_file)

    with open(test_file, 'rb') as file_object:
      result = analyzer_helper.AnalyzeFileObject(file_object)

    self.assertEqual(result, definitions.TYPE_INDICATOR_AFF4)

    test_file = self._GetTestFilePath(['aff4', 'dream.aff4'])
    self._SkipIfPathNotExists(test_file)

    with open(test_file, 'rb') as file_object:
      result = analyzer_helper.AnalyzeFileObject(file_object)

    self.assertIsNone(result)


if __name__ == '__main__':
  unittest.main()
