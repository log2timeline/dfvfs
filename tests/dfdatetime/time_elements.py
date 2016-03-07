#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the time elements implementation."""

import unittest

from dfvfs.dfdatetime import time_elements


class PosixTimeTest(unittest.TestCase):
  """Tests for the POSIX timestamp object."""

  def testCopyToStatObject(self):
    """Tests the CopyToStatObject function."""
    time_elements_object = time_elements.TimeElements(
        (2010, 8, 12, 20, 6, 31))

    expected_stat_time_tuple = (1281643591, 0)
    stat_time_tuple = time_elements_object.CopyToStatObject()
    self.assertEqual(stat_time_tuple, expected_stat_time_tuple)


if __name__ == '__main__':
  unittest.main()
