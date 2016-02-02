#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the CPIO path specification implementation."""

import unittest

from dfvfs.path import cpio_path_spec

from tests.path import test_lib


class CPIOPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the CPIO path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = cpio_path_spec.CPIOPathSpec(
        location=u'/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      _ = cpio_path_spec.CPIOPathSpec(location=u'/test', parent=None)

    with self.assertRaises(ValueError):
      _ = cpio_path_spec.CPIOPathSpec(location=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      _ = cpio_path_spec.CPIOPathSpec(
          location=u'/test', parent=self._path_spec, bogus=u'BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = cpio_path_spec.CPIOPathSpec(
        location=u'/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = u'\n'.join([
        u'type: TEST',
        u'type: CPIO, location: /test',
        u''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
