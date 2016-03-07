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

  # TODO: move parts of this method into base class.
  def CopyFromString(self, time_string):
    """Copies a FILETIME from a string containing a date and time value.

    Args:
      time_string: A string containing a date and time value formatted as:
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

    # The time string should at least contain 'YYYY-MM-DD'.
    if (time_string_length < 10 or time_string[4] != u'-' or
        time_string[7] != u'-'):
      raise ValueError(u'Invalid time string.')

    # If a time of day is specified the time string it should at least
    # contain 'YYYY-MM-DD hh:mm:ss'.
    if (time_string_length > 10 and (
        time_string_length < 19 or time_string[10] != u' ' or
        time_string[13] != u':' or time_string[16] != u':')):
      raise ValueError(u'Invalid time string.')

    try:
      year = int(time_string[0:4], 10)
    except ValueError:
      raise ValueError(u'Unable to parse year.')

    try:
      month = int(time_string[5:7], 10)
    except ValueError:
      raise ValueError(u'Unable to parse month.')

    if month not in range(1, 13):
      raise ValueError(u'Month value out of bounds.')

    try:
      day_of_month = int(time_string[8:10], 10)
    except ValueError:
      raise ValueError(u'Unable to parse day of month.')

    if day_of_month not in range(1, 32):
      raise ValueError(u'Day of month value out of bounds.')

    hours = 0
    minutes = 0
    seconds = 0

    if time_string_length > 10:
      try:
        hours = int(time_string[11:13], 10)
      except ValueError:
        raise ValueError(u'Unable to parse hours.')

      if hours not in range(0, 24):
        raise ValueError(u'Hours value out of bounds.')

      try:
        minutes = int(time_string[14:16], 10)
      except ValueError:
        raise ValueError(u'Unable to parse minutes.')

      if minutes not in range(0, 60):
        raise ValueError(u'Minutes value out of bounds.')

      try:
        seconds = int(time_string[17:19], 10)
      except ValueError:
        raise ValueError(u'Unable to parse day of seconds.')

      if seconds not in range(0, 60):
        raise ValueError(u'Seconds value out of bounds.')

    micro_seconds = 0
    timezone_offset = 0

    if time_string_length > 19:
      if time_string[19] != u'.':
        timezone_index = 19
      else:
        for timezone_index in range(19, time_string_length):
          if time_string[timezone_index] in [u'+', u'-']:
            break

          # The calculation that follow rely on the timezone index to point
          # beyond the string in case no timezone offset was defined.
          if timezone_index == time_string_length - 1:
            timezone_index += 1

      if timezone_index > 19:
        fraction_of_seconds_length = timezone_index - 20
        if fraction_of_seconds_length not in [3, 6]:
          raise ValueError(u'Invalid time string.')

        try:
          micro_seconds = int(time_string[20:timezone_index], 10)
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
