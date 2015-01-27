#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the VSS path specification implementation."""

import unittest

from dfvfs.path import test_lib
from dfvfs.path import vshadow_path_spec


class VShadowPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the VSS path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = vshadow_path_spec.VShadowPathSpec(parent=self._path_spec)

    self.assertNotEquals(path_spec, None)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/vss2', parent=self._path_spec)

    self.assertNotEquals(path_spec, None)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._path_spec)

    self.assertNotEquals(path_spec, None)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/vss2', store_index=1, parent=self._path_spec)

    self.assertNotEquals(path_spec, None)

    with self.assertRaises(ValueError):
      _ = vshadow_path_spec.VShadowPathSpec(parent=None)

    with self.assertRaises(ValueError):
      _ = vshadow_path_spec.VShadowPathSpec(
          parent=self._path_spec, bogus=u'BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = vshadow_path_spec.VShadowPathSpec(parent=self._path_spec)

    self.assertNotEquals(path_spec, None)

    expected_comparable = u'\n'.join([
        u'type: TEST',
        u'type: VSHADOW',
        u''])

    self.assertEquals(path_spec.comparable, expected_comparable)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/vss2', parent=self._path_spec)

    self.assertNotEquals(path_spec, None)

    expected_comparable = u'\n'.join([
        u'type: TEST',
        u'type: VSHADOW, location: /vss2',
        u''])

    self.assertEquals(path_spec.comparable, expected_comparable)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._path_spec)

    self.assertNotEquals(path_spec, None)

    expected_comparable = u'\n'.join([
        u'type: TEST',
        u'type: VSHADOW, store index: 1',
        u''])

    self.assertEquals(path_spec.comparable, expected_comparable)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/vss2', store_index=1, parent=self._path_spec)

    self.assertNotEquals(path_spec, None)

    expected_comparable = u'\n'.join([
        u'type: TEST',
        u'type: VSHADOW, location: /vss2, store index: 1',
        u''])

    self.assertEquals(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
