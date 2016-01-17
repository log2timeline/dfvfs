# -*- coding: utf-8 -*-
"""The data range path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class DataRangePathSpec(path_spec.PathSpec):
  """Class that implements the data range path specification.

  Attributes:
    range_offset: integer containing the start offset of the data range.
    range_size: integer containing the size of the data range.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_DATA_RANGE

  def __init__(self, range_offset=None, range_size=None, parent=None, **kwargs):
    """Initializes the path specification object.

    Note that the data range path specification must have a parent.

    Args:
      range_offset: optional integer containing the start offset of the data
                    range.
      range_size: optional integer containing the size of the data range.
      parent: optional parent path specification (instance of PathSpec).
      kwargs: a dictionary of keyword arguments dependending on the path
              specification.

    Raises:
      ValueError: when range offset, range offset or parent are not set.
    """
    if not range_offset or not range_size or not parent:
      raise ValueError(u'Missing range offset, range size or parent value.')

    super(DataRangePathSpec, self).__init__(parent=parent, **kwargs)
    self.range_offset = range_offset
    self.range_size = range_size

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    sub_comparable_string = (
        u'range_offset: 0x{0:08x}, range_size: 0x{1:08x}').format(
            self.range_offset, self.range_size)
    return self._GetComparable(sub_comparable_string=sub_comparable_string)


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(DataRangePathSpec)
