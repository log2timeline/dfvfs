# -*- coding: utf-8 -*-
"""The CPIO path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import location_path_spec


class CPIOPathSpec(location_path_spec.LocationPathSpec):
  """Class that implements the CPIO file path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_CPIO

  def __init__(self, location=None, parent=None, **kwargs):
    """Initializes the path specification object.

    Note that the CPIO file path specification must have a parent.

    Args:
      location (Optional[str]): CPIO file internal location string prefixed
          with a path separator character.
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError(u'Missing parent value.')

    super(CPIOPathSpec, self).__init__(
        location=location, parent=parent, **kwargs)


factory.Factory.RegisterPathSpec(CPIOPathSpec)
