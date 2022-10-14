# -*- coding: utf-8 -*-
"""The location-based path specification implementation."""

from dfvfs.path import path_spec


class LocationPathSpec(path_spec.PathSpec):
  """Base class for location-based path specifications.

  Attributes:
    location (str): location.
  """

  def __init__(self, location=None, parent=None, **kwargs):
    """Initializes a path specification.

    Args:
      location (Optional[str]): location.
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when location is not set.
    """
    if not location:
      raise ValueError('Missing location value.')

    super(LocationPathSpec, self).__init__(parent=parent, **kwargs)
    self.location = location

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    return self._GetComparable(sub_comparable_string=(
        f'location: {self.location:s}'))
