#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the POSIX timestamp implementation."""

import unittest

from dfvfs.dfdatetime import posix_time


class PosixTimeTest(unittest.TestCase):
  """Tests for the POSIX timestamp object."""

  def testCopyToStatObject(self):
    """Tests the CopyToStatObject function."""
    posix_time_object = posix_time.PosixTime(1281643591, micro_seconds=546875)

    expected_stat_time_tuple = (1281643591, 5468750)
    stat_time_tuple = posix_time_object.CopyToStatObject()
    self.assertEqual(stat_time_tuple, expected_stat_time_tuple)


if __name__ == '__main__':
  unittest.main()
