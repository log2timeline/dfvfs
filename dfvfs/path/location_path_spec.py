# -*- coding: utf-8 -*-
"""The location-based path specification implementation."""

from dfvfs.path import path_spec


class LocationPathSpec(path_spec.PathSpec):
  """Base class for location-based path specifications.

  Attributes:
    location: string containing the location.
  """

  def __init__(self, location=None, parent=None, **kwargs):
    """Initializes the path specification object.

    Args:
      location: optional string containing the location.
      parent: optional parent path specification (instance of PathSpec),
              default is None.
      kwargs: a dictionary of keyword arguments dependending on the path
              specification.

    Raises:
      ValueError: when location is not set.
    """
    if not location:
      raise ValueError(u'Missing location value.')

    super(LocationPathSpec, self).__init__(parent=parent, **kwargs)
    self.location = location

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    sub_comparable_string = u'location: {0:s}'.format(self.location)
    return self._GetComparable(sub_comparable_string=sub_comparable_string)
