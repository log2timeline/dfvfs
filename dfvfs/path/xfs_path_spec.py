# -*- coding: utf-8 -*-
"""The XFS path specification implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class XFSPathSpec(path_spec.PathSpec):
  """XFS path specification implementation.

  Attributes:
    inode (int): inode.
    location (str): location.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_XFS

  def __init__(
      self, inode=None, location=None, parent=None, **kwargs):
    """Initializes a path specification.

    Note that an XFS path specification must have a parent.

    Args:
      inode (Optional[int]): inode.
      location (Optional[str]): location.
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when parent or both inode and location are not set.
    """
    if (not inode and not location) or not parent:
      raise ValueError('Missing inode and location, or parent value.')

    super(XFSPathSpec, self).__init__(parent=parent, **kwargs)
    self.inode = inode
    self.location = location

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    string_parts = []

    if self.inode is not None:
      string_parts.append('inode: {0:d}'.format(self.inode))
    if self.location is not None:
      string_parts.append('location: {0:s}'.format(self.location))

    return self._GetComparable(sub_comparable_string=', '.join(string_parts))


factory.Factory.RegisterPathSpec(XFSPathSpec)
