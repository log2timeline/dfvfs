#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the zip path specification implementation."""

import unittest

from tests.path import test_lib
from dfvfs.path import zip_path_spec


class ZipPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the zip path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = zip_path_spec.ZipPathSpec(
        location=u'/test', parent=self._path_spec)

    self.assertNotEquals(path_spec, None)

    with self.assertRaises(ValueError):
      _ = zip_path_spec.ZipPathSpec(location=u'/test', parent=None)

    with self.assertRaises(ValueError):
      _ = zip_path_spec.ZipPathSpec(location=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      _ = zip_path_spec.ZipPathSpec(
          location=u'/test', parent=self._path_spec, bogus=u'BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = zip_path_spec.ZipPathSpec(
        location=u'/test', parent=self._path_spec)

    self.assertNotEquals(path_spec, None)

    expected_comparable = u'\n'.join([
        u'type: TEST',
        u'type: ZIP, location: /test',
        u''])

    self.assertEquals(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
