#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Keramics path specification implementation."""

import unittest

from dfvfs.path import keramics_path_spec

from tests.path import test_lib


class KeramicsPathSpecTest(test_lib.PathSpecTestCase):
    """Tests for the Keramics path specification implementation."""

    def testInitialize(self):
        """Tests the path specification initialization."""
        path_spec = keramics_path_spec.KeramicsPathSpec(location="/test", parent=None)

        self.assertIsNotNone(path_spec)

        with self.assertRaises(ValueError):
            keramics_path_spec.KeramicsPathSpec(parent=None)

        with self.assertRaises(ValueError):
            keramics_path_spec.KeramicsPathSpec(bogus="BOGUS", parent=None)

    def testComparable(self):
        """Tests the path specification comparable property."""
        path_spec = keramics_path_spec.KeramicsPathSpec(location="/test", parent=None)

        self.assertIsNotNone(path_spec)

        expected_comparable = "\n".join(["type: KERAMICS, location: /test", ""])

        self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == "__main__":
    unittest.main()
