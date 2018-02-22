#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the VHD image path specification implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import vhdi_path_spec

from tests.path import test_lib


class VHDIPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the VHD image path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = vhdi_path_spec.VHDIPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      vhdi_path_spec.VHDIPathSpec(parent=None)

    with self.assertRaises(ValueError):
      vhdi_path_spec.VHDIPathSpec(parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = vhdi_path_spec.VHDIPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: VHDI',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
