# -*- coding: utf-8 -*-
"""The FAT path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class FATPathSpec(path_spec.PathSpec):
  """FAT path specification implementation.

  Attributes:
    identifier (int): (virtual) identifier.
    location (str): location.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FAT

  def __init__(
      self, identifier=None, location=None, parent=None, **kwargs):
    """Initializes a path specification.

    Note that an FAT path specification must have a parent.

    Args:
      identifier (Optional[int]): (virtual) identifier.
      location (Optional[str]): location.
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when parent or both identifier and location are not set.
    """
    if (not identifier and not location) or not parent:
      raise ValueError('Missing identifier and location, or parent value.')

    super(FATPathSpec, self).__init__(parent=parent, **kwargs)
    self.identifier = identifier
    self.location = location

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    string_parts = []

    if self.identifier is not None:
      string_parts.append(f'identifier: {self.identifier:d}')
    if self.location is not None:
      string_parts.append(f'location: {self.location:s}')

    return self._GetComparable(sub_comparable_string=', '.join(string_parts))


factory.Factory.RegisterPathSpec(FATPathSpec)
