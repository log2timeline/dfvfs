# -*- coding: utf-8 -*-
"""The operating system path specification implementation."""

from __future__ import unicode_literals

import os

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import location_path_spec


class OSPathSpec(location_path_spec.LocationPathSpec):
  """Operating system path specification."""

  _IS_SYSTEM_LEVEL = True
  TYPE_INDICATOR = definitions.TYPE_INDICATOR_OS

  def __init__(self, location=None, **kwargs):
    """Initializes a path specification.

    Note that the operating system path specification cannot have a parent.

    Args:
      location (Optional[str]): operating specific location string e.g.
          /opt/dfvfs or C:\\Opt\\dfvfs.

    Raises:
      ValueError: when location is not set or parent is set.
    """
    if not location:
      raise ValueError('Missing location value.')

    parent = None
    if 'parent' in kwargs:
      parent = kwargs['parent']
      del kwargs['parent']

    if parent:
      raise ValueError('Parent value set.')

    # Within the path specification the path should be absolute.
    location = os.path.abspath(location)

    super(OSPathSpec, self).__init__(location=location, parent=parent, **kwargs)


factory.Factory.RegisterPathSpec(OSPathSpec)
