#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the operating system path specification implementation."""

import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import test_lib


class OSPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the operating system path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = os_path_spec.OSPathSpec(location=u'/test')

    self.assertNotEquals(path_spec, None)

    with self.assertRaises(ValueError):
      _ = os_path_spec.OSPathSpec(location=u'/test', parent=self._path_spec)

    with self.assertRaises(ValueError):
      _ = os_path_spec.OSPathSpec(location=u'/test', bogus=u'BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = os_path_spec.OSPathSpec(location=u'/test')

    self.assertNotEquals(path_spec, None)

    expected_comparable = u'\n'.join([
        u'type: OS, location: /test',
        u''])

    self.assertEquals(path_spec.comparable, expected_comparable)

  def testIsSystemLevel(self):
    """Tests the IsSystemLevel function."""
    path_spec = os_path_spec.OSPathSpec(location=u'/test')

    self.assertNotEquals(path_spec, None)
    self.assertTrue(path_spec.IsSystemLevel())


if __name__ == '__main__':
  unittest.main()
