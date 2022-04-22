# -*- coding: utf-8 -*-
"""The path Overlay specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class OverlayPathSpec(path_spec.PathSpec):
  """Overlay path specification.

  Attributes:
    location (str): location.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_OVERLAY

  def __init__(self, location=None, parent=None, **kwargs):
    """Initializes an Overlay path specification.

    Args:
      location (Optional[str]): location.
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when location and parent are not set.
    """
    if not parent and not location:
      raise ValueError('Missing location, or parent value.')

    super(OverlayPathSpec, self).__init__(parent=parent, **kwargs)
    self.location = location

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    string_parts = []

    if self.location is not None:
      string_parts.append('location: {0:s}'.format(self.location))

    return self._GetComparable(sub_comparable_string=', '.join(string_parts))


factory.Factory.RegisterPathSpec(OverlayPathSpec)
