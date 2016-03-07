# -*- coding: utf-8 -*-
"""Date and time values interface."""

import abc


class DateTimeValues(object):
  """Class that defines the date time values interface."""

  @abc.abstractmethod
  def CopyToStatObject(self):
    """Copies the timestamp to a stat object timestamp.

    Returns:
      A tuple of an integer containing a POSIX timestamp in seconds
      and an integer containing the remainder in 100 nano seconds or
      None on error.
    """
