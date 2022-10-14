# -*- coding: utf-8 -*-
"""The EXT path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class EXTPathSpec(path_spec.PathSpec):
  """EXT path specification implementation.

  Attributes:
    inode (int): inode.
    location (str): location.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_EXT

  def __init__(
      self, inode=None, location=None, parent=None, **kwargs):
    """Initializes a path specification.

    Note that an EXT path specification must have a parent.

    Args:
      inode (Optional[int]): inode.
      location (Optional[str]): location.
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when parent or both inode and location are not set.
    """
    if (not inode and not location) or not parent:
      raise ValueError('Missing inode and location, or parent value.')

    super(EXTPathSpec, self).__init__(parent=parent, **kwargs)
    self.inode = inode
    self.location = location

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    string_parts = []

    if self.inode is not None:
      string_parts.append(f'inode: {self.inode:d}')
    if self.location is not None:
      string_parts.append(f'location: {self.location:s}')

    return self._GetComparable(sub_comparable_string=', '.join(string_parts))


factory.Factory.RegisterPathSpec(EXTPathSpec)
