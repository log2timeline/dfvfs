# -*- coding: utf-8 -*-
"""The Logical Volume Manager (LVM) path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class LVMPathSpec(path_spec.PathSpec):
  """LVM path specification.

  Attributes:
    location (str): location.
    volume_index (int): logical volume index.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_LVM

  def __init__(self, location=None, parent=None, volume_index=None, **kwargs):
    """Initializes a path specification.

    Note that the LVM path specification must have a parent.

    Args:
      location (Optional[str]): location.
      parent (Optional[PathSpec]): parent path specification.
      volume_index (Optional[int]): logical volume index.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError('Missing parent value.')

    super(LVMPathSpec, self).__init__(parent=parent, **kwargs)
    self.location = location
    self.volume_index = volume_index

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    string_parts = []

    if self.location is not None:
      string_parts.append(f'location: {self.location:s}')
    if self.volume_index is not None:
      string_parts.append(f'volume index: {self.volume_index:d}')

    return self._GetComparable(sub_comparable_string=', '.join(string_parts))


factory.Factory.RegisterPathSpec(LVMPathSpec)
