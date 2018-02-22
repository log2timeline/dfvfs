#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the TAR path specification implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import tar_path_spec

from tests.path import test_lib


class TARPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the TAR path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = tar_path_spec.TARPathSpec(
        location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      tar_path_spec.TARPathSpec(location='/test', parent=None)

    with self.assertRaises(ValueError):
      tar_path_spec.TARPathSpec(location=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      tar_path_spec.TARPathSpec(
          location='/test', parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = tar_path_spec.TARPathSpec(
        location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: TAR, location: /test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
