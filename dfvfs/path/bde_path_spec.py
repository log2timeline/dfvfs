# -*- coding: utf-8 -*-
"""The BitLocker Drive Encryption (BDE) path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class BDEPathSpec(path_spec.PathSpec):
  """Class that implements the BDE path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BDE

  def __init__(self, credentials=None, parent=None, **kwargs):
    """Initializes the path specification object.

    Note that the BDE path specification must have a parent.

    Args:
      credentials: optional dictionary of credentials.
      parent: optional parent path specification (instance of PathSpec).

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError(u'Missing parent value.')

    super(BDEPathSpec, self).__init__(parent=parent, **kwargs)
    self.credentials = credentials

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    string_parts = []

    if self.credentials is not None:
      for credential, value in iter(sorted(self.credentials.items())):
        string_parts.append(u'{0:s}: {1!s}'.format(credential, value))

    return self._GetComparable(sub_comparable_string=u', '.join(string_parts))


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(BDEPathSpec)
