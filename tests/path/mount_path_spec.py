#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the mount path specification implementation."""

import unittest

from dfvfs.path import mount_path_spec

from tests.path import test_lib


class MountPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the operating system path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = mount_path_spec.MountPathSpec(identifier='C')

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      mount_path_spec.MountPathSpec()

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = mount_path_spec.MountPathSpec(identifier='C')

    self.assertIsNotNone(path_spec)

    expected_comparable = 'type: MOUNT, identifier: C\n'

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
