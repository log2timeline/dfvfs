#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the PHDI image path specification implementation."""

import unittest

from dfvfs.path import phdi_path_spec

from tests.path import test_lib


class PHDIPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the PHDI image path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = phdi_path_spec.PHDIPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      phdi_path_spec.PHDIPathSpec(parent=None)

    with self.assertRaises(ValueError):
      phdi_path_spec.PHDIPathSpec(parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = phdi_path_spec.PHDIPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: PHDI',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
