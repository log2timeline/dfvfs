# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) partition path specification implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class TSKPartitionPathSpec(path_spec.PathSpec):
  """SleuthKit (TSK) partition path specification.

  Attributes:
    location (str): location.
    part_index (int): part index.
    start_offset (int): start offset.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK_PARTITION

  def __init__(
      self, location=None, parent=None, part_index=None, start_offset=None,
      **kwargs):
    """Initializes a path specification.

    Note that the TSK partition path specification must have a parent.

    Args:
      location (Optional[str]): location.
      parent (Optional[PathSpec]): parent path specification.
      part_index (Optional[int]): part index.
      start_offset (Optional[int]): start offset.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError('Missing parent value.')

    super(TSKPartitionPathSpec, self).__init__(parent=parent, **kwargs)
    self.location = location
    self.part_index = part_index
    self.start_offset = start_offset

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    string_parts = []

    if self.location is not None:
      string_parts.append('location: {0:s}'.format(self.location))
    if self.part_index is not None:
      string_parts.append('part index: {0:d}'.format(self.part_index))
    if self.start_offset is not None:
      string_parts.append('start offset: 0x{0:08x}'.format(self.start_offset))

    return self._GetComparable(sub_comparable_string=', '.join(string_parts))


factory.Factory.RegisterPathSpec(TSKPartitionPathSpec)
