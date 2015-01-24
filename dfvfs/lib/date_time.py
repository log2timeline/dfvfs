# -*- coding: utf-8 -*-
"""The date and time definitions."""

import calendar
import time


class PosixTimestamp(object):
  """Class that implements a POSIX timestamp.

  The POSIX timestamp is a signed integer that contains the number of
  seconds since 1970-01-01 00:00:00 (also known as the POSIX epoch).
  Negative values represent date and times predating the POSIX epoch.

  The POSIX timestamp was initialliy 32-bit though 64-bit variants
  are known to be used.
  """

  # The difference between Jan 1, 1601 and Jan 1, 1970 in seconds.
  _FILETIME_TO_POSIX_BASE = 11644473600L
  _INT64_MAX = (1 << 63L) - 1

  @classmethod
  def FromFiletime(cls, filetime):
    """Copies a FILETIME to a POSIX timestamp.

    The FILETIME is a 64-bit integer that contains the number of 100th nano
    seconds since 1601-01-01 00:00:00. Technically FILETIME consists of
    2 x 32-bit parts and is presumed to be unsigned.

    Args:
      filetime: a named tuple containg the time elements.

    Returns:
      An integer containing a POSIX timestamp or None
    """
    if filetime < 0:
      return

    timestamp, _ = divmod(filetime, 10000000)
    timestamp -= cls._FILETIME_TO_POSIX_BASE
    if timestamp > cls._INT64_MAX:
      return
    return timestamp

  @classmethod
  def FromTimeElements(cls, time_elements_tuple):
    """Copies a timestamp from the time elements tuple.

    Args:
      time_elements_tuple: a named tuple containg the time elements.

    Returns:
      An integer containing a POSIX timestamp.
    """
    return calendar.timegm(time_elements_tuple)

  @classmethod
  def GetNow(cls):
    """Retrieves the current time (now) as a timestamp in UTC."""
    time_elements = time.gmtime()
    return calendar.timegm(time_elements)
