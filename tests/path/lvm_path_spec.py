#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the LVM path specification implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import lvm_path_spec

from tests.path import test_lib


class LVMPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the LVM path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = lvm_path_spec.LVMPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/lvm2', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._path_spec, volume_index=1)

    self.assertIsNotNone(path_spec)

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/lvm2', parent=self._path_spec, volume_index=1)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      lvm_path_spec.LVMPathSpec(parent=None)

    with self.assertRaises(ValueError):
      lvm_path_spec.LVMPathSpec(
          parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = lvm_path_spec.LVMPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: LVM',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/lvm2', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: LVM, location: /lvm2',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = lvm_path_spec.LVMPathSpec(
        parent=self._path_spec, volume_index=1)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: LVM, volume index: 1',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/lvm2', parent=self._path_spec, volume_index=1)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: LVM, location: /lvm2, volume index: 1',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
