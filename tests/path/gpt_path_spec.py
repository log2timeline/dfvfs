#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the GPT path specification implementation."""

import unittest

from dfvfs.path import gpt_path_spec

from tests.path import test_lib


class GPTPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the GPT path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = gpt_path_spec.GPTPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = gpt_path_spec.GPTPathSpec(
        location='/gpt2', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = gpt_path_spec.GPTPathSpec(
        entry_index=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = gpt_path_spec.GPTPathSpec(
        entry_index=1, location='/gpt2', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      gpt_path_spec.GPTPathSpec(parent=None)

    with self.assertRaises(ValueError):
      gpt_path_spec.GPTPathSpec(
          parent=self._path_spec, bogus='BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = gpt_path_spec.GPTPathSpec(parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: GPT',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = gpt_path_spec.GPTPathSpec(
        location='/gpt2', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: GPT, location: /gpt2',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = gpt_path_spec.GPTPathSpec(
        entry_index=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: GPT, entry index: 1',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = gpt_path_spec.GPTPathSpec(
        entry_index=1, location='/gpt2', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = '\n'.join([
        'type: TEST',
        'type: GPT, entry index: 1, location: /gpt2',
        ''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
