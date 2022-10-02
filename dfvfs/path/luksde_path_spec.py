# -*- coding: utf-8 -*-
"""The LUKS Drive Encryption path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class LUKSDEPathSpec(path_spec.PathSpec):
  """LUKSDE path specification.

  Attributes:
    password (str): password.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_LUKSDE

  def __init__(self, password=None, parent=None, **kwargs):
    """Initializes a path specification.

    Note that the LUKSDE path specification must have a parent.

    Args:
      password (Optional[str]): password.
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError('Missing parent value.')

    super(LUKSDEPathSpec, self).__init__(parent=parent, **kwargs)
    self.password = password

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    string_parts = []

    if self.password:
      string_parts.append(f'password: {self.password:s}')

    return self._GetComparable(sub_comparable_string=', '.join(string_parts))


factory.Factory.RegisterPathSpec(LUKSDEPathSpec)
