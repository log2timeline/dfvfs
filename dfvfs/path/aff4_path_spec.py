# -*- coding: utf-8 -*-
"""The AFF4 image path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class AFF4PathSpec(path_spec.PathSpec):
  """AFF4 image path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_AFF4

  def __init__(self, parent=None, **kwargs):
    """Initializes a path specification.

    Note that the AFF4 file path specification must have a parent.

    Args:
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError('Missing parent value.')

    super(AFF4PathSpec, self).__init__(parent=parent, **kwargs)


factory.Factory.RegisterPathSpec(AFF4PathSpec)
