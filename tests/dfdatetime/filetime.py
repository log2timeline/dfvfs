#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Filetime timestamp implementation."""

import unittest

from dfvfs.dfdatetime import filetime


class FiletimeTest(unittest.TestCase):
  """Tests for the Filetime timestamp object."""

  def testCopyFromString(self):
    """Tests the CopyFromString function."""
    filetime_object = filetime.Filetime()

    expected_timestamp = 0x1cb39b14e8c4000
    filetime_object.CopyFromString(u'2010-08-12')
    self.assertEqual(filetime_object.timestamp, expected_timestamp)

    expected_timestamp = 0x1cb3a623cb6a580
    filetime_object.CopyFromString(u'2010-08-12 21:06:31')
    self.assertEqual(filetime_object.timestamp, expected_timestamp)

    expected_timestamp = 0x01cb3a623d0a17ce
    filetime_object.CopyFromString(u'2010-08-12 21:06:31.546875')
    self.assertEqual(filetime_object.timestamp, expected_timestamp)

    expected_timestamp = 0x1cb3a6a9ece7fce
    filetime_object.CopyFromString(u'2010-08-12 21:06:31.546875-01:00')
    self.assertEqual(filetime_object.timestamp, expected_timestamp)

    expected_timestamp = 0x1cb3a59db45afce
    filetime_object.CopyFromString(u'2010-08-12 21:06:31.546875+01:00')
    self.assertEqual(filetime_object.timestamp, expected_timestamp)

    expected_timestamp = 86400 * 10000000
    filetime_object.CopyFromString(u'1601-01-02 00:00:00')
    self.assertEqual(filetime_object.timestamp, expected_timestamp)

    with self.assertRaises(ValueError):
      filetime_object.CopyFromString(u'')

    with self.assertRaises(ValueError):
      filetime_object.CopyFromString(u'195a-01-02')

    with self.assertRaises(ValueError):
      filetime_object.CopyFromString(u'10000-01-02')

    with self.assertRaises(ValueError):
      filetime_object.CopyFromString(u'1601-01-32')

    with self.assertRaises(ValueError):
      filetime_object.CopyFromString(u'1601-01-b2')

    with self.assertRaises(ValueError):
      filetime_object.CopyFromString(u'1601-13-02')

    with self.assertRaises(ValueError):
      filetime_object.CopyFromString(u'1601-a1-02')

    with self.assertRaises(ValueError):
      filetime_object.CopyFromString(u'1601-01-02 14:00')

    with self.assertRaises(ValueError):
      filetime_object.CopyFromString(u'1601-01-02 24:00:00')

    with self.assertRaises(ValueError):
      filetime_object.CopyFromString(u'1601-01-02 1s:00:00')

    with self.assertRaises(ValueError):
      filetime_object.CopyFromString(u'1601-01-02 00:60:00')

    with self.assertRaises(ValueError):
      filetime_object.CopyFromString(u'1601-01-02 00:e0:00')

    with self.assertRaises(ValueError):
      filetime_object.CopyFromString(u'1601-01-02 00:00:60')

    with self.assertRaises(ValueError):
      filetime_object.CopyFromString(u'1601-01-02 00:00:w0')

  # TODO: add tests for CopyToStatObject.


if __name__ == '__main__':
  unittest.main()
