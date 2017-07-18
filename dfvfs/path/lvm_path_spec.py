# -*- coding: utf-8 -*-
"""The Logical Volume Manager (LVM) path specification implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class LVMPathSpec(path_spec.PathSpec):
  """LVM path specification.

  Attributes:
    location (str): location.
    volume_index (int): volume index.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_LVM

  def __init__(self, location=None, parent=None, volume_index=None, **kwargs):
    """Initializes a path specification.

    Note that the LVM path specification must have a parent.

    Args:
      location (Optional[str]): location.
      parent (Optional[PathSpec]): parent path specification.
      volume_index (Optional[int]): volume index.

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
      string_parts.append('location: {0:s}'.format(self.location))
    if self.volume_index is not None:
      string_parts.append('volume index: {0:d}'.format(self.volume_index))

    return self._GetComparable(sub_comparable_string=', '.join(string_parts))


factory.Factory.RegisterPathSpec(LVMPathSpec)
