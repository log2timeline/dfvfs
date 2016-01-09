# -*- coding: utf-8 -*-
"""The mount path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class MountPathSpec(path_spec.PathSpec):
  """Class that implements the mount path specification.

  Attributes:
    identifier: string containing the identifier of the mount point.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_MOUNT

  def __init__(self, identifier, **kwargs):
    """Initializes the path specification object.

    Note that the mount path specification cannot have a parent.

    Args:
      identifier: string containing the identifier of the mount point.
      kwargs: a dictionary of keyword arguments dependending on the path
              specification.

    Raises:
      ValueError: when identifier is not set.
    """
    if not identifier:
      raise ValueError(u'Missing identifier value.')

    super(MountPathSpec, self).__init__(parent=None, **kwargs)
    self.identifier = identifier

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    sub_comparable_string = u'identifier: {0:s}'.format(self.identifier)
    return self._GetComparable(sub_comparable_string=sub_comparable_string)


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(MountPathSpec)
