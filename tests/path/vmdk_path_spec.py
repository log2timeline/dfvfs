#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the VMDK image path specification implementation."""

import unittest

from dfvfs.path import vmdk_path_spec

from tests.path import test_lib


class VMDKPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the VMDK image path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = vmdk_path_spec.VMDKPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      vmdk_path_spec.VMDKPathSpec(parent=None)

    with self.assertRaises(ValueError):
      vmdk_path_spec.VMDKPathSpec(parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = vmdk_path_spec.VMDKPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: VMDK',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
