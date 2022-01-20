#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the CS path specification implementation."""

import unittest

from dfvfs.path import cs_path_spec

from tests.path import test_lib


class CSPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the CS path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = cs_path_spec.CSPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = cs_path_spec.CSPathSpec(
        location='/cs2', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = cs_path_spec.CSPathSpec(
        parent=self._path_spec, volume_index=1)

    self.assertIsNotNone(path_spec)

    path_spec = cs_path_spec.CSPathSpec(
        location='/cs2', parent=self._path_spec, volume_index=1)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      cs_path_spec.CSPathSpec(parent=None)

    with self.assertRaises(ValueError):
      cs_path_spec.CSPathSpec(
          parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = cs_path_spec.CSPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: CS',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = cs_path_spec.CSPathSpec(
        location='/cs2', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: CS, location: /cs2',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = cs_path_spec.CSPathSpec(
        parent=self._path_spec, volume_index=1)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: CS, volume index: 1',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = cs_path_spec.CSPathSpec(
        location='/cs2', parent=self._path_spec, volume_index=1)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: CS, location: /cs2, volume index: 1',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
