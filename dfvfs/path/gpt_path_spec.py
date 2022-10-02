# -*- coding: utf-8 -*-
"""The GUID Partition Table (GPT) path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class GPTPathSpec(path_spec.PathSpec):
  """GPT path specification.

  Attributes:
    entry_index (int): partition entry index.
    location (str): location.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_GPT

  def __init__(self, location=None, entry_index=None, parent=None, **kwargs):
    """Initializes a path specification.

    Note that the GPT path specification must have a parent.

    Args:
      entry_index (Optional[int]): partition entry index.
      location (Optional[str]): location.
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError('Missing parent value.')

    super(GPTPathSpec, self).__init__(parent=parent, **kwargs)
    self.entry_index = entry_index
    self.location = location

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    string_parts = []

    if self.entry_index is not None:
      string_parts.append(f'entry index: {self.entry_index:d}')
    if self.location is not None:
      string_parts.append(f'location: {self.location:s}')

    return self._GetComparable(sub_comparable_string=', '.join(string_parts))


factory.Factory.RegisterPathSpec(GPTPathSpec)
