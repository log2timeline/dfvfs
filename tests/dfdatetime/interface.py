#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the date and time values interface."""

import unittest

from dfvfs.dfdatetime import interface


class DateTimeValuesTest(unittest.TestCase):
  """Tests for the date and time values interface."""

  def testCopyDateFromString(self):
    """Tests the CopyDateFromString function."""
    date_time_values = interface.DateTimeValues()

    expected_date_tuple = (2010, 8, 12)
    date_tuple = date_time_values._CopyDateFromString(u'2010-08-12')
    self.assertEqual(date_tuple, expected_date_tuple)

    expected_date_tuple = (1601, 1, 2)
    date_tuple = date_time_values._CopyDateFromString(u'1601-01-02')
    self.assertEqual(date_tuple, expected_date_tuple)

    with self.assertRaises(ValueError):
      date_time_values._CopyDateFromString(u'')

    with self.assertRaises(ValueError):
      date_time_values._CopyDateFromString(u'195a-01-02')

    with self.assertRaises(ValueError):
      date_time_values._CopyDateFromString(u'10000-01-02')

    with self.assertRaises(ValueError):
      date_time_values._CopyDateFromString(u'1601-01-32')

    with self.assertRaises(ValueError):
      date_time_values._CopyDateFromString(u'1601-01-b2')

    with self.assertRaises(ValueError):
      date_time_values._CopyDateFromString(u'1601-13-02')

    with self.assertRaises(ValueError):
      date_time_values._CopyDateFromString(u'1601-a1-02')

    with self.assertRaises(ValueError):
      date_time_values._CopyDateFromString(u'2010-02-29')

    with self.assertRaises(ValueError):
      date_time_values._CopyDateFromString(u'2010-04-31')

  def testCopyTimeFromString(self):
    """Tests the CopyTimeFromString function."""
    date_time_values = interface.DateTimeValues()

    expected_time_tuple = (8, 4, 32, 0, 0)
    time_tuple = date_time_values._CopyTimeFromString(u'08:04:32')
    self.assertEqual(time_tuple, expected_time_tuple)

    expected_time_tuple = (20, 23, 56, 0, 0)
    time_tuple = date_time_values._CopyTimeFromString(u'20:23:56')
    self.assertEqual(time_tuple, expected_time_tuple)

    expected_time_tuple = (20, 23, 56, 0, -19800)
    time_tuple = date_time_values._CopyTimeFromString(u'20:23:56+05:30')
    self.assertEqual(time_tuple, expected_time_tuple)

    expected_time_tuple = (20, 23, 56, 327000, 0)
    time_tuple = date_time_values._CopyTimeFromString(u'20:23:56.327')
    self.assertEqual(time_tuple, expected_time_tuple)

    expected_time_tuple = (20, 23, 56, 327000, -3600)
    time_tuple = date_time_values._CopyTimeFromString(u'20:23:56.327+01:00')
    self.assertEqual(time_tuple, expected_time_tuple)

    expected_time_tuple = (20, 23, 56, 327124, 0)
    time_tuple = date_time_values._CopyTimeFromString(u'20:23:56.327124')
    self.assertEqual(time_tuple, expected_time_tuple)

    expected_time_tuple = (20, 23, 56, 327124, 18000)
    time_tuple = date_time_values._CopyTimeFromString(u'20:23:56.327124-05:00')
    self.assertEqual(time_tuple, expected_time_tuple)

    with self.assertRaises(ValueError):
      date_time_values._CopyTimeFromString(u'')

    with self.assertRaises(ValueError):
      date_time_values._CopyTimeFromString(u'14')

    with self.assertRaises(ValueError):
      date_time_values._CopyTimeFromString(u'14:00')

    with self.assertRaises(ValueError):
      date_time_values._CopyTimeFromString(u'24:00:00')

    with self.assertRaises(ValueError):
      date_time_values._CopyTimeFromString(u'1s:00:00')

    with self.assertRaises(ValueError):
      date_time_values._CopyTimeFromString(u'00:60:00')

    with self.assertRaises(ValueError):
      date_time_values._CopyTimeFromString(u'00:e0:00')

    with self.assertRaises(ValueError):
      date_time_values._CopyTimeFromString(u'00:00:60')

    with self.assertRaises(ValueError):
      date_time_values._CopyTimeFromString(u'00:00:w0')

  def testGetDaysPerMonth(self):
    """Tests the GetDaysPerMonth function."""
    date_time_values = interface.DateTimeValues()

    expected_days_per_month = list(interface.DateTimeValues._DAYS_PER_MONTH)

    days_per_month = []
    for month in range(1, 13):
      days_per_month.append(
          date_time_values._GetDaysPerMonth(1999, month))

    self.assertEqual(days_per_month, expected_days_per_month)

    expected_days_per_month[1] += 1

    days_per_month = []
    for month in range(1, 13):
      days_per_month.append(
          date_time_values._GetDaysPerMonth(2000, month))

    self.assertEqual(days_per_month, expected_days_per_month)

    with self.assertRaises(ValueError):
      date_time_values._GetDaysPerMonth(1999, 0)

    with self.assertRaises(ValueError):
      date_time_values._GetDaysPerMonth(1999, 13)

  def testIsLeapYear(self):
    """Tests the IsLeapYear function."""
    date_time_values = interface.DateTimeValues()

    self.assertFalse(date_time_values._IsLeapYear(1999))
    self.assertTrue(date_time_values._IsLeapYear(2000))
    self.assertTrue(date_time_values._IsLeapYear(1996))


if __name__ == '__main__':
  unittest.main()
