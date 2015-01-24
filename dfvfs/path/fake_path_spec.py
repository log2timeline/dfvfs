# -*- coding: utf-8 -*-
"""The fake path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import location_path_spec


class FakePathSpec(location_path_spec.LocationPathSpec):
  """Class that implements the fake path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FAKE

  def __init__(self, location=None, **kwargs):
    """Initializes the path specification object.

       Note that the fake path specification cannot have a parent.

    Args:
      location: optional location string e.g. /opt/dfvfs. The default is None.
      kwargs: a dictionary of keyword arguments dependending on the path
              specification.
    """
    super(FakePathSpec, self).__init__(location=location, parent=None, **kwargs)


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(FakePathSpec)
