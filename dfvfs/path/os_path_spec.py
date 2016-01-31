# -*- coding: utf-8 -*-
"""The operating system path specification implementation."""

import os

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import location_path_spec


class OSPathSpec(location_path_spec.LocationPathSpec):
  """Class that implements the operating system path specification."""

  _IS_SYSTEM_LEVEL = True
  TYPE_INDICATOR = definitions.TYPE_INDICATOR_OS

  def __init__(self, location=None, **kwargs):
    """Initializes the path specification object.

    Note that the operating system path specification cannot have a parent.

    Args:
      location: optional operating specific location string e.g. /opt/dfvfs or
                C:\\Opt\\dfvfs.
      kwargs: a dictionary of keyword arguments dependending on the path
              specification.

    Raises:
      ValueError: when location is not set or parent is set.
    """
    if not location:
      raise ValueError(u'Missing location value.')

    parent = None
    if u'parent' in kwargs:
      parent = kwargs[u'parent']
      del kwargs[u'parent']

    if parent:
      raise ValueError(u'Parent value set.')

    # Within the path specification the path should be absolute.
    location = os.path.abspath(location)

    super(OSPathSpec, self).__init__(location=location, parent=parent, **kwargs)


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(OSPathSpec)
