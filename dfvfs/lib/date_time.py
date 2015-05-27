# -*- coding: utf-8 -*-
"""The date and time definitions."""

import abc
import calendar
import time


class DateTimeValues(object):
  """Class that implements the date time values interface."""

  @abc.abstractmethod
  def CopyToStatObject(self):
    """Copies the timestamp to a stat object timestamp.

    Returns:
      A tuple of an integer containing a POSIX timestamp in seconds
      and an integer containing the remainder in 100 nano seconds or
      None on error.
    """


class FakeDateTimeValues(object):
  """Class that implements the fake file system date time values."""

  def CopyToStatObject(self):
    """Copies the timestamp to a stat object timestamp.

    Returns:
      A tuple of an integer containing a POSIX timestamp in seconds
      and an integer containing the remainder in 100 nano seconds or
      None on error.
    """
    time_elements = time.gmtime()
    return calendar.timegm(time_elements), 0


class Filetime(DateTimeValues):
  """Class that implements a FILETIME timestamp.

  The FILETIME is a 64-bit integer that contains the number of 100th nano
  seconds since 1601-01-01 00:00:00. Technically FILETIME is a structure
  that consists of 2 x 32-bit integers and is presumed to be unsigned.
  """

  # The difference between Jan 1, 1601 and Jan 1, 1970 in seconds.
  _FILETIME_TO_POSIX_BASE = 11644473600L
  _INT64_MAX = (1 << 63L) - 1

  def __init__(self, timestamp):
    """Initializes the FILETIME object.

    Args:
      timestamp: the FILETIME timestamp.
    """
    super(Filetime, self).__init__()
    self._timestamp = timestamp

  def CopyToStatObject(self):
    """Copies the timestamp to a stat object timestamp.

    Returns:
      A tuple of an integer containing a POSIX timestamp in seconds
      and an integer containing the remainder in 100 nano seconds or
      None on error.
    """
    if self._timestamp < 0:
      return None, None

    timestamp, _ = divmod(self._timestamp, 10)
    timestamp, micro_seconds = divmod(timestamp, 1000000)
    timestamp -= self._FILETIME_TO_POSIX_BASE
    if timestamp > self._INT64_MAX:
      return None, None
    return timestamp, micro_seconds


class PosixTimestamp(DateTimeValues):
  """Class that implements a POSIX timestamp.

  The POSIX timestamp is a signed integer that contains the number of
  seconds since 1970-01-01 00:00:00 (also known as the POSIX epoch).
  Negative values represent date and times predating the POSIX epoch.

  The POSIX timestamp was initialliy 32-bit though 64-bit variants
  are known to be used.
  """

  def __init__(self, timestamp):
    """Initializes the POSIX timestamp object.

    Args:
      timestamp: the FILETIME timestamp.
    """
    super(PosixTimestamp, self).__init__()
    self._timestamp = timestamp

  def CopyToStatObject(self):
    """Copies the timestamp to a stat object timestamp.

    Returns:
      A tuple of an integer containing a POSIX timestamp in seconds
      and an integer containing the remainder in 100 nano seconds or
      None on error.
    """
    return self._posix_time, 0


class TimeElements(DateTimeValues):
  """Class that implements a time elements timestamp."""

  def __init__(self, time_elements_tuple):
    """Initializes the time elements object.

    Args:
      time_elements_tuple: a named tuple containg the time elements.
    """
    super(TimeElements, self).__init__()
    self._time_elements_tuple = time_elements_tuple

  def CopyToStatObject(self):
    """Copies the timestamp to a stat object timestamp.

    Returns:
      A tuple of an integer containing a POSIX timestamp in seconds
      and an integer containing the remainder in 100 nano seconds or
      None on error.
    """
    return calendar.timegm(self._time_elements_tuple), 0
