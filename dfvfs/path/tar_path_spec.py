# -*- coding: utf-8 -*-
"""The tar path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import location_path_spec


class TarPathSpec(location_path_spec.LocationPathSpec):
  """Class that implements the tar file path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TAR

  def __init__(self, location=None, parent=None, **kwargs):
    """Initializes the path specification object.

       Note that the tar file path specification must have a parent.

    Args:
      location: optional tar file internal location string prefixed with a path
                separator character.
      parent: optional parent path specification (instance of PathSpec).
      kwargs: a dictionary of keyword arguments dependending on the path
              specification.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError(u'Missing parent value.')

    super(TarPathSpec, self).__init__(
        location=location, parent=parent, **kwargs)


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(TarPathSpec)
