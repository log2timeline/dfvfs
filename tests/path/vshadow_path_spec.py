#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the VSS path specification implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import vshadow_path_spec

from tests.path import test_lib


class VShadowPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the VSS path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = vshadow_path_spec.VShadowPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location='/vss2', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location='/vss2', store_index=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      vshadow_path_spec.VShadowPathSpec(parent=None)

    with self.assertRaises(ValueError):
      vshadow_path_spec.VShadowPathSpec(
          parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = vshadow_path_spec.VShadowPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: VSHADOW',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location='/vss2', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: VSHADOW, location: /vss2',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: VSHADOW, store index: 1',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location='/vss2', store_index=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: VSHADOW, location: /vss2, store index: 1',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
