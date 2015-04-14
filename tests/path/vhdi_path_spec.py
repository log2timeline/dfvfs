#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the VHD image path specification implementation."""

import unittest

from tests.path import test_lib
from dfvfs.path import vhdi_path_spec


class VhdiPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the VHD image path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = vhdi_path_spec.VhdiPathSpec(parent=self._path_spec)

    self.assertNotEquals(path_spec, None)

    with self.assertRaises(ValueError):
      _ = vhdi_path_spec.VhdiPathSpec(parent=None)

    with self.assertRaises(ValueError):
      _ = vhdi_path_spec.VhdiPathSpec(parent=self._path_spec, bogus=u'BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = vhdi_path_spec.VhdiPathSpec(parent=self._path_spec)

    self.assertNotEquals(path_spec, None)

    expected_comparable = u'\n'.join([
        u'type: TEST',
        u'type: VHDI',
        u''])

    self.assertEquals(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
