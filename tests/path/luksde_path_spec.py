#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the LUKSDE path specification implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import luksde_path_spec

from tests.path import test_lib


class LUKSDEPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the LUKSDE path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = luksde_path_spec.LUKSDEPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      luksde_path_spec.LUKSDEPathSpec(parent=None)

    with self.assertRaises(ValueError):
      luksde_path_spec.LUKSDEPathSpec(parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = luksde_path_spec.LUKSDEPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: LUKSDE',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
