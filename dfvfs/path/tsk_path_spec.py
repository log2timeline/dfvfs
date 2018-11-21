# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) path specification implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class TSKPathSpec(path_spec.PathSpec):
  """SleuthKit (TSK) path specification.

  Attributes:
    data_stream (str): data stream name, where None indicates the default
        data stream.
    inode (int): inode.
    location (str): location.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK

  def __init__(
      self, data_stream=None, inode=None, location=None, parent=None, **kwargs):
    """Initializes a path specification.

    Note that the TSK path specification must have a parent.

    Args:
      data_stream (Optional[str]): data stream name, where None indicates
          the default data stream.
      inode (Optional[int]): inode.
      location (Optional[str]): location.
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when inode and location, or parent are not set.
    """
    # Note that pytsk/libtsk overloads inode and a value of 0 is valid in
    # contrast to an ext file system.
    if (inode is None and not location) or not parent:
      raise ValueError('Missing inode and location, or parent value.')

    super(TSKPathSpec, self).__init__(parent=parent, **kwargs)
    self.data_stream = data_stream
    self.inode = inode
    self.location = location

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    string_parts = []

    if self.data_stream:
      string_parts.append('data stream: {0:s}'.format(self.data_stream))
    if self.inode is not None:
      string_parts.append('inode: {0:d}'.format(self.inode))
    if self.location is not None:
      string_parts.append('location: {0:s}'.format(self.location))

    return self._GetComparable(sub_comparable_string=', '.join(string_parts))


factory.Factory.RegisterPathSpec(TSKPathSpec)
