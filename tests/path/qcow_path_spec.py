#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the QCOW image path specification implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import qcow_path_spec

from tests.path import test_lib


class QCOWPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the QCOW image path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = qcow_path_spec.QCOWPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      qcow_path_spec.QCOWPathSpec(parent=None)

    with self.assertRaises(ValueError):
      qcow_path_spec.QCOWPathSpec(parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = qcow_path_spec.QCOWPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: QCOW',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
