#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the APM path specification implementation."""

import unittest

from dfvfs.path import apm_path_spec

from tests.path import test_lib


class APMPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the APM path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = apm_path_spec.APMPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = apm_path_spec.APMPathSpec(
        location='/apm2', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = apm_path_spec.APMPathSpec(
        entry_index=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = apm_path_spec.APMPathSpec(
        entry_index=1, location='/apm2', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      apm_path_spec.APMPathSpec(parent=None)

    with self.assertRaises(ValueError):
      apm_path_spec.APMPathSpec(
          parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = apm_path_spec.APMPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: APM',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = apm_path_spec.APMPathSpec(
        location='/apm2', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: APM, location: /apm2',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = apm_path_spec.APMPathSpec(
        entry_index=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: APM, entry index: 1',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = apm_path_spec.APMPathSpec(
        entry_index=1, location='/apm2', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: APM, entry index: 1, location: /apm2',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
