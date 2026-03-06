#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the AFF4 path specification implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import aff4_path_spec
from dfvfs.path import factory

from tests.path import test_lib


class AFF4PathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the AFF4 path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = aff4_path_spec.AFF4PathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      aff4_path_spec.AFF4PathSpec(parent=None)

    with self.assertRaises(ValueError):
      aff4_path_spec.AFF4PathSpec(parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = aff4_path_spec.AFF4PathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: AFF4',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

  def testFactoryNewPathSpec(self):
    """Tests the path specification factory."""
    path_spec = factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_AFF4, parent=self._path_spec)

    self.assertIsInstance(path_spec, aff4_path_spec.AFF4PathSpec)


if __name__ == '__main__':
  unittest.main()
