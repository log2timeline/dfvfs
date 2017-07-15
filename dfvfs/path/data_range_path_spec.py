# -*- coding: utf-8 -*-
"""The data range path specification implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class DataRangePathSpec(path_spec.PathSpec):
  """Data range path specification.

  Attributes:
    range_offset (int): start offset of the data range.
    range_size (int): size of the data range.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_DATA_RANGE

  def __init__(self, parent=None, range_offset=None, range_size=None, **kwargs):
    """Initializes a path specification.

    Note that the data range path specification must have a parent.

    Args:
      parent (Optional[PathSpec]): parent path specification.
      range_offset (Optional[int]): start offset of the data range.
      range_size (Optional[int]): size of the data range.

    Raises:
      ValueError: when range offset, range offset or parent are not set.
    """
    if not range_offset or not range_size or not parent:
      raise ValueError('Missing range offset, range size or parent value.')

    super(DataRangePathSpec, self).__init__(parent=parent, **kwargs)
    self.range_offset = range_offset
    self.range_size = range_size

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    sub_comparable_string = (
        'range_offset: 0x{0:08x}, range_size: 0x{1:08x}').format(
            self.range_offset, self.range_size)
    return self._GetComparable(sub_comparable_string=sub_comparable_string)


factory.Factory.RegisterPathSpec(DataRangePathSpec)
