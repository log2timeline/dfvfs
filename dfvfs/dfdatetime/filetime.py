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

  def _CopyTimeFromString(self, time_string, time_string_length):
    """Copies a time from a string.

    Args:
      time_string: a string containing a time value formatted as:
                   hh:mm:ss.######[+-]##:##
                   Where # are numeric digits ranging from 0 to 9 and the
                   seconds fraction can be either 3 or 6 digits. The seconds
                   fraction and timezone offset are optional.
      time_string_length: an integer containing the length of the time string.

    Returns:
      A tuple of integers containing hours, minutes, seconds, microseconds,
      timezone offset in seconds.

    Raises:
      ValueError: if the time string is invalid or not supported.
    """
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
          timezone_offset = int(time_string[
              timezone_index + 1:timezone_index + 3])
        except ValueError:
          raise ValueError(u'Unable to parse timezone hours offset.')

        if timezone_offset not in range(0, 24):
          raise ValueError(u'Timezone hours offset value out of bounds.')

        # Note that when the sign of the timezone offset is negative
        # the difference needs to be added. We do so by flipping the sign.
        if time_string[timezone_index] == u'-':
          timezone_offset *= 60
        else:
          timezone_offset *= -60

        try:
          timezone_offset += int(time_string[
              timezone_index + 4:timezone_index + 6])
        except ValueError:
          raise ValueError(u'Unable to parse timezone minutes offset.')

        timezone_offset *= 60

    return hours, minutes, seconds, micro_seconds, timezone_offset

  # TODO: move parts of this method into base class.
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

    year, month, day_of_month = self._CopyDateFromString(
        time_string, time_string_length)

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

      hours, minutes, seconds, microseconds, timezone_offset = (
          self._CopyTimeFromString(time_string[11:], time_string_length - 11))

    self.timestamp = int(calendar.timegm((
        year, month, day_of_month, hours, minutes, seconds)))

    self.timestamp += timezone_offset + self._FILETIME_TO_POSIX_BASE
    self.timestamp = (self.timestamp * 1000000) + micro_seconds
    self.timestamp *= 10

  def CopyToStatObject(self):
    """Copies the timestamp to a stat object timestamp.

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
