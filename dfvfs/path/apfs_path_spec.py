# -*- coding: utf-8 -*-
"""The APFS path specification implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class APFSPathSpec(path_spec.PathSpec):
  """APFS path specification implementation.

  Attributes:
    identifier (int): identifier.
    location (str): location.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_APFS

  def __init__(
      self, identifier=None, location=None, parent=None, **kwargs):
    """Initializes a path specification.

    Note that an APFS path specification must have a parent.

    Args:
      identifier (Optional[int]): identifier.
      location (Optional[str]): location.
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when parent or both identifier and location are not set.
    """
    if (not identifier and not location) or not parent:
      raise ValueError('Missing identifier and location, or parent value.')

    super(APFSPathSpec, self).__init__(parent=parent, **kwargs)
    self.identifier = identifier
    self.location = location

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    string_parts = []

    if self.identifier is not None:
      string_parts.append('identifier: {0:d}'.format(self.identifier))
    if self.location is not None:
      string_parts.append('location: {0:s}'.format(self.location))

    return self._GetComparable(sub_comparable_string=', '.join(string_parts))


factory.Factory.RegisterPathSpec(APFSPathSpec)
