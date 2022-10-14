# -*- coding: utf-8 -*-
"""The HFS path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class HFSPathSpec(path_spec.PathSpec):
  """HFS path specification implementation.

  Attributes:
    data_stream (str): data stream name, where None indicates the default
        data stream.
    identifier (int): catalog node identifier (CNID).
    location (str): location.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_HFS

  def __init__(
      self, data_stream=None, identifier=None, location=None, parent=None,
      **kwargs):
    """Initializes a path specification.

    Note that an HFS path specification must have a parent.

    Args:
      data_stream (Optional[str]): data stream name, where None indicates
          the default data stream.
      identifier (Optional[int]): catalog node identifier (CNID).
      location (Optional[str]): location.
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when parent or both identifier and location are not set.
    """
    if (not identifier and not location) or not parent:
      raise ValueError('Missing identifier and location, or parent value.')

    super(HFSPathSpec, self).__init__(parent=parent, **kwargs)
    self.data_stream = data_stream
    self.identifier = identifier
    self.location = location

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    string_parts = []

    if self.data_stream:
      string_parts.append(f'data stream: {self.data_stream:s}')
    if self.identifier is not None:
      string_parts.append(f'identifier: {self.identifier:d}')
    if self.location is not None:
      string_parts.append(f'location: {self.location:s}')

    return self._GetComparable(sub_comparable_string=', '.join(string_parts))


factory.Factory.RegisterPathSpec(HFSPathSpec)
