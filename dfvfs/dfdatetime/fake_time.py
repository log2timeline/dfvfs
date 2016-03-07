# -*- coding: utf-8 -*-
"""Fake timestamp implementation."""

import calendar
import time

from dfvfs.dfdatetime import interface


class FakeTime(interface.DateTimeValues):
  """Class that implements a fake timestamp."""

  def CopyToStatObject(self):
    """Copies the timestamp to a stat object timestamp.

    Returns:
      A tuple of an integer containing a POSIX timestamp in seconds
      and an integer containing the remainder in 100 nano seconds or
      None on error.
    """
    time_elements = time.gmtime()
    return calendar.timegm(time_elements), 0
