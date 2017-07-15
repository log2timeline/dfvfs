# -*- coding: utf-8 -*-
"""The Volume Shadow Snapshots (VSS) path specification implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class VShadowPathSpec(path_spec.PathSpec):
  """Volume Shadow Snapshots (VSS) path specification.

  Attributes:
    location (str): location.
    store_index (int): store index.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VSHADOW

  def __init__(self, location=None, parent=None, store_index=None, **kwargs):
    """Initializes a path specification.

    Note that the VSS path specification must have a parent.

    Args:
      location (Optional[str]): location.
      parent (Optional[PathSpec]): parent path specification.
      store_index (Optional[int]): store index.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError('Missing parent value.')

    super(VShadowPathSpec, self).__init__(parent=parent, **kwargs)
    self.location = location
    self.store_index = store_index

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    string_parts = []

    if self.location is not None:
      string_parts.append('location: {0:s}'.format(self.location))
    if self.store_index is not None:
      string_parts.append('store index: {0:d}'.format(self.store_index))

    return self._GetComparable(sub_comparable_string=', '.join(string_parts))


factory.Factory.RegisterPathSpec(VShadowPathSpec)
