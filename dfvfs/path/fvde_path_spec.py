# -*- coding: utf-8 -*-
"""The FileVault Drive Encryption (FVDE) path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class FVDEPathSpec(path_spec.PathSpec):
  """Class that implements the FVDE path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FVDE

  def __init__(self, parent=None, **kwargs):
    """Initializes the path specification object.

    Note that the FVDE path specification must have a parent.

    Args:
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError(u'Missing parent value.')

    super(FVDEPathSpec, self).__init__(parent=parent, **kwargs)

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    return self._GetComparable()


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(FVDEPathSpec)
