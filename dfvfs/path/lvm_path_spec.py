# -*- coding: utf-8 -*-
"""The Logical Volume Manager (LVM) path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class LVMPathSpec(path_spec.PathSpec):
  """Class that implements the LVM path specification.

  Attributes:
    location: string containing the location.
    volume_index: integer containing the volume index.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_LVM

  def __init__(self, location=None, parent=None, volume_index=None, **kwargs):
    """Initializes the path specification object.

    Note that the LVM path specification must have a parent.

    Args:
      location: optional string containing the location.
      parent: optional parent path specification (instance of PathSpec).
      volume_index: optional integer containing the volume index.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError(u'Missing parent value.')

    super(LVMPathSpec, self).__init__(parent=parent, **kwargs)
    self.location = location
    self.volume_index = volume_index

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    string_parts = []

    if self.location is not None:
      string_parts.append(u'location: {0:s}'.format(self.location))
    if self.volume_index is not None:
      string_parts.append(u'volume index: {0:d}'.format(self.volume_index))

    return self._GetComparable(sub_comparable_string=u', '.join(string_parts))


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(LVMPathSpec)
