# -*- coding: utf-8 -*-
"""The PHDI image path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class PHDIPathSpec(path_spec.PathSpec):
  """PHDI image path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_PHDI

  def __init__(self, parent=None, **kwargs):
    """Initializes a path specification.

    Note that the PHDI file path specification must have a parent.

    Args:
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError('Missing parent value.')

    super(PHDIPathSpec, self).__init__(parent=parent, **kwargs)


factory.Factory.RegisterPathSpec(PHDIPathSpec)
