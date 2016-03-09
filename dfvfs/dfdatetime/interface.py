# -*- coding: utf-8 -*-
"""Date and time values interface."""

import abc


class DateTimeValues(object):
  """Class that defines the date time values interface."""

  _DAYS_PER_MONTH = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

  def _CopyDateFromString(self, date_string):
    """Copies a date from a string.

    Args:
      date_string: a string containing a date value formatted as:
                   YYYY-MM-DD

    Returns:
      A tuple of integers containing year, month, day of month.

    Raises:
      ValueError: if the date string is invalid or not supported.
    """
    date_string_length = len(date_string)

    # The date string should at least contain 'YYYY-MM-DD'.
    if (date_string_length < 10 or date_string[4] != u'-' or
        date_string[7] != u'-'):
      raise ValueError(u'Invalid date string.')

    try:
      year = int(date_string[0:4], 10)
    except ValueError:
      raise ValueError(u'Unable to parse year.')

    try:
      month = int(date_string[5:7], 10)
    except ValueError:
      raise ValueError(u'Unable to parse month.')

    try:
      day_of_month = int(date_string[8:10], 10)
    except ValueError:
      raise ValueError(u'Unable to parse day of month.')

    days_per_month = self._GetDaysPerMonth(year, month)
    if day_of_month not in range(1, days_per_month):
      raise ValueError(u'Day of month value out of bounds.')

    return year, month, day_of_month

  def _CopyTimeFromString(self, time_string):
    """Copies a time from a string.

    Args:
      time_string: a string containing a time value formatted as:
                   hh:mm:ss.######[+-]##:##
                   Where # are numeric digits ranging from 0 to 9 and the
                   seconds fraction can be either 3 or 6 digits. The seconds
                   fraction and timezone offset are optional.

    Returns:
      A tuple of integers containing hours, minutes, seconds, microseconds,
      timezone offset in seconds.

    Raises:
      ValueError: if the time string is invalid or not supported.
    """
    time_string_length = len(time_string)

    # The time string should at least contain 'hh:mm:ss'.
    if (time_string_length < 8 or time_string[2] != u':' or
        time_string[5] != u':'):
      raise ValueError(u'Invalid time string.')

    try:
      hours = int(time_string[0:2], 10)
    except ValueError:
      raise ValueError(u'Unable to parse hours.')

    if hours not in range(0, 24):
      raise ValueError(u'Hours value out of bounds.')

    try:
      minutes = int(time_string[3:5], 10)
    except ValueError:
      raise ValueError(u'Unable to parse minutes.')

    if minutes not in range(0, 60):
      raise ValueError(u'Minutes value out of bounds.')

    try:
      seconds = int(time_string[6:8], 10)
    except ValueError:
      raise ValueError(u'Unable to parse day of seconds.')

    if seconds not in range(0, 60):
      raise ValueError(u'Seconds value out of bounds.')

    micro_seconds = 0
    timezone_offset = 0

    if time_string_length > 8:
      if time_string[8] != u'.':
        timezone_index = 8
      else:
        for timezone_index in range(8, time_string_length):
          if time_string[timezone_index] in (u'+', u'-'):
            break

          # The calculation that follow rely on the timezone index to point
          # beyond the string in case no timezone offset was defined.
          if timezone_index == time_string_length - 1:
            timezone_index += 1

      if timezone_index > 8:
        fraction_of_seconds_length = timezone_index - 9
        if fraction_of_seconds_length not in (3, 6):
          raise ValueError(u'Invalid time string.')

        try:
          micro_seconds = int(time_string[9:timezone_index], 10)
        except ValueError:
          raise ValueError(u'Unable to parse fraction of seconds.')

        if fraction_of_seconds_length == 3:
          micro_seconds *= 1000

      if timezone_index < time_string_length:
        if (time_string_length - timezone_index != 6 or
            time_string[timezone_index + 3] != u':'):
          raise ValueError(u'Invalid time string.')

        try:
          timezone_offset = int(
              time_string[timezone_index + 1:timezone_index + 3])
        except ValueError:
          raise ValueError(u'Unable to parse timezone hours offset.')

        if timezone_offset not in range(0, 24):
          raise ValueError(u'Timezone hours offset value out of bounds.')

        timezone_offset *= 60

        try:
          timezone_offset += int(
              time_string[timezone_index + 4:timezone_index + 6])
        except ValueError:
          raise ValueError(u'Unable to parse timezone minutes offset.')

        # Note that when the sign of the timezone offset is negative
        # the difference needs to be added. We do so by flipping the sign.
        if time_string[timezone_index] == u'-':
          timezone_offset *= 60
        else:
          timezone_offset *= -60

    return hours, minutes, seconds, micro_seconds, timezone_offset

  def _GetDaysPerMonth(self, year, month):
    """Retrieves the number of days in a month of a specific year.

    Args:
      year: an integer containing the year.
      month: an integer containing the month ranging from 1 to 12.

    Returns:
      An integer containing the number of days in the month.

    Raises:
      ValueError: if the month value is out of bounds.
    """
    if month not in range(1, 13):
      raise ValueError(u'Month value out of bounds.')

    days_per_month = self._DAYS_PER_MONTH[month - 1]
    if month == 2 and self._IsLeapYear(year):
      days_per_month += 1

    return days_per_month

  def _IsLeapYear(self, year):
    """Determines if a year is a leap year.

    Args:
      year: an integer containing the year.

    Returns:
      A boolean value indicating if the year is a leap year.
    """
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0

  @abc.abstractmethod
  def CopyToStatTimeTuple(self):
    """Copies the timestamp to a stat timestamp tuple.

    Returns:
      A tuple of an integer containing a POSIX timestamp in seconds
      and an integer containing the remainder in 100 nano seconds or
      None on error.
    """
