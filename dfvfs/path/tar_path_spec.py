# -*- coding: utf-8 -*-
"""The TAR path specification implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import location_path_spec


class TARPathSpec(location_path_spec.LocationPathSpec):
  """TAR file path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TAR

  def __init__(self, location=None, parent=None, **kwargs):
    """Initializes a path specification.

    Note that the TAR file path specification must have a parent.

    Args:
      location (str): TAR file internal location string prefixed with a path
          separator character.
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError('Missing parent value.')

    super(TARPathSpec, self).__init__(
        location=location, parent=parent, **kwargs)


factory.Factory.RegisterPathSpec(TARPathSpec)
