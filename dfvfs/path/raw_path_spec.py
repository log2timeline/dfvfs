# -*- coding: utf-8 -*-
"""The RAW storage media image path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class RawPathSpec(path_spec.PathSpec):
  """Class that implements the RAW storage media image path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_RAW

  def __init__(self, parent=None, **kwargs):
    """Initializes the path specification object.

    Note that the RAW path specification must have a parent.

    Args:
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError(u'Missing parent value.')

    super(RawPathSpec, self).__init__(parent=parent, **kwargs)

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    return self._GetComparable()


factory.Factory.RegisterPathSpec(RawPathSpec)
