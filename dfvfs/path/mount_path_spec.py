# -*- coding: utf-8 -*-
"""The mount path specification implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class MountPathSpec(path_spec.PathSpec):
  """Mount path specification.

  Attributes:
    identifier (str): identifier of the mount point.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_MOUNT

  def __init__(self, identifier, **kwargs):
    """Initializes a path specification.

    Note that the mount path specification cannot have a parent.

    Args:
      identifier (str): identifier of the mount point.

    Raises:
      ValueError: when identifier is not set.
    """
    if not identifier:
      raise ValueError('Missing identifier value.')

    super(MountPathSpec, self).__init__(parent=None, **kwargs)
    self.identifier = identifier

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    sub_comparable_string = 'identifier: {0:s}'.format(self.identifier)
    return self._GetComparable(sub_comparable_string=sub_comparable_string)


factory.Factory.RegisterPathSpec(MountPathSpec)
