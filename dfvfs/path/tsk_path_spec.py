# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class TSKPathSpec(path_spec.PathSpec):
  """Class that implements the SleuthKit (TSK) path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK

  def __init__(
      self, data_stream=None, inode=None, location=None, parent=None, **kwargs):
    """Initializes the path specification object.

       Note that the TSK path specification must have a parent.

    Args:
      data_stream: optional data stream name. The default is None, which
                   indicates the default data stream.
      inode: optional inode. The default is None.
      location: optional location string. The default is None.
      parent: optional parent path specification (instance of PathSpec),
              The default is None.
      kwargs: a dictionary of keyword arguments dependending on the path
              specification

    Raises:
      ValueError: when inode and location, or parent are not set.
    """
    if (not inode and not location) or not parent:
      raise ValueError(u'Missing inode and location, or parent value.')

    super(TSKPathSpec, self).__init__(parent=parent, **kwargs)
    self.data_stream = data_stream
    self.inode = inode
    self.location = location

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    string_parts = []

    if self.data_stream is not None:
      string_parts.append(u'data stream: {0:s}'.format(self.data_stream))
    if self.inode is not None:
      string_parts.append(u'inode: {0:d}'.format(self.inode))
    if self.location is not None:
      string_parts.append(u'location: {0:s}'.format(self.location))

    return self._GetComparable(sub_comparable_string=u', '.join(string_parts))


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(TSKPathSpec)
