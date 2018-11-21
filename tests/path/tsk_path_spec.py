#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the TSK path specification implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import tsk_path_spec

from tests.path import test_lib


class TSKPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the TSK path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = tsk_path_spec.TSKPathSpec(
        location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = tsk_path_spec.TSKPathSpec(
        data_stream='test', location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = tsk_path_spec.TSKPathSpec(
        inode=0, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = tsk_path_spec.TSKPathSpec(
        location='/test', inode=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      tsk_path_spec.TSKPathSpec(location='/test', parent=None)

    with self.assertRaises(ValueError):
      tsk_path_spec.TSKPathSpec(location=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      tsk_path_spec.TSKPathSpec(inode=None, parent=self._path_spec)

    with self.assertRaises(ValueError):
      tsk_path_spec.TSKPathSpec(
          location='/test', parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = tsk_path_spec.TSKPathSpec(
        location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: TSK, location: /test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = tsk_path_spec.TSKPathSpec(
        data_stream='test', location='/test', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: TSK, data stream: test, location: /test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = tsk_path_spec.TSKPathSpec(
        inode=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: TSK, inode: 1',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = tsk_path_spec.TSKPathSpec(
        location='/test', inode=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: TSK, inode: 1, location: /test',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
