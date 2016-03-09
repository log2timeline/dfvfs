# -*- coding: utf-8 -*-
"""FILETIME timestamp implementation."""

import calendar

from dfvfs.dfdatetime import interface


class Filetime(interface.DateTimeValues):
  """Class that implements a FILETIME timestamp.

  The FILETIME timestamp is a 64-bit integer that contains the number
  of 100th nano seconds since 1601-01-01 00:00:00.

  Do not confuse this with the FILETIME structure that consists of
  2 x 32-bit integers and is presumed to be unsigned.

  Attributes:
    timestamp: the FILETIME timestamp.
  """

  # The difference between Jan 1, 1601 and Jan 1, 1970 in seconds.
  _FILETIME_TO_POSIX_BASE = 11644473600
  _INT64_MAX = (1 << 63) - 1

  def __init__(self, timestamp=None):
    """Initializes a FILETIME object.

    Args:
      timestamp: optional FILETIME timestamp.
    """
    super(Filetime, self).__init__()
    self.timestamp = timestamp

  def CopyFromString(self, time_string):
    """Copies a FILETIME from a string containing a date and time value.

    Args:
      time_string: a string containing a date and time value formatted as:
                   YYYY-MM-DD hh:mm:ss.######[+-]##:##
                   Where # are numeric digits ranging from 0 to 9 and the
                   seconds fraction can be either 3 or 6 digits. The time
                   of day, seconds fraction and timezone offset are optional.
                   The default timezone is UTC.

    Returns:
      An integer containing the timestamp.

    Raises:
      ValueError: if the time string is invalid or not supported.
    """
    if not time_string:
      raise ValueError(u'Invalid time string.')

    time_string_length = len(time_string)

    year, month, day_of_month = self._CopyDateFromString(time_string)

    hours = 0
    minutes = 0
    seconds = 0
    micro_seconds = 0
    timezone_offset = 0

    if time_string_length > 10:
      # If a time of day is specified the time string it should at least
      # contain 'YYYY-MM-DD hh:mm:ss'.
      if time_string[10] != u' ':
        raise ValueError(u'Invalid time string.')

      hours, minutes, seconds, micro_seconds, timezone_offset = (
          self._CopyTimeFromString(time_string[11:]))

    self.timestamp = int(calendar.timegm((
        year, month, day_of_month, hours, minutes, seconds)))

    self.timestamp += timezone_offset + self._FILETIME_TO_POSIX_BASE
    self.timestamp = (self.timestamp * 1000000) + micro_seconds
    self.timestamp *= 10

  def CopyToStatTimeTuple(self):
    """Copies the timestamp to a stat timestamp tuple.

    Returns:
      A tuple of an integer containing a POSIX timestamp in seconds
      and an integer containing the remainder in 100 nano seconds or
      None on error.
    """
    if self.timestamp < 0:
      return None, None

    timestamp, remainder = divmod(self.timestamp, 10000000)
    timestamp -= self._FILETIME_TO_POSIX_BASE
    if timestamp > self._INT64_MAX:
      return None, None
    return timestamp, remainder
