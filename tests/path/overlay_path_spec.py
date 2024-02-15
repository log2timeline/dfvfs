#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Overlay path specification implementation."""

import unittest

from dfvfs.path import overlay_path_spec

from tests.path import test_lib


class OverlayPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the OVERLAY path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = overlay_path_spec.OverlayPathSpec(
        location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = overlay_path_spec.OverlayPathSpec(
        location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      overlay_path_spec.OverlayPathSpec(
          location='/test', parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = overlay_path_spec.OverlayPathSpec(
        location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: OVERLAY, location: /test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
