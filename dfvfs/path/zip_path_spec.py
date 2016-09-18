# -*- coding: utf-8 -*-
"""The zip path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import location_path_spec


class ZipPathSpec(location_path_spec.LocationPathSpec):
  """Class that implements the zip file path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ZIP

  def __init__(self, location=None, parent=None, **kwargs):
    """Initializes the path specification.

    Note that the zip file path specification must have a parent.

    Args:
      location (Optional[str]): ZIP file internal location string prefixed
          with a path separator character.
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError(u'Missing parent value.')

    super(ZipPathSpec, self).__init__(
        location=location, parent=parent, **kwargs)


factory.Factory.RegisterPathSpec(ZipPathSpec)
