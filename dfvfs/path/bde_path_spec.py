# -*- coding: utf-8 -*-
"""The BitLocker Drive Encryption (BDE) path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class BDEPathSpec(path_spec.PathSpec):
  """BDE path specification.

  Attributes:
    password (str): password.
    recovery_password (str): recovery password.
    startup_key (str): name of the startup key file.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BDE

  def __init__(
      self, password=None, parent=None, recovery_password=None,
      startup_key=None, **kwargs):
    """Initializes a path specification.

    Note that the BDE path specification must have a parent.

    Args:
      password (Optional[str]): password.
      parent (Optional[PathSpec]): parent path specification.
      recovery_password (Optional[str]): recovery password.
      startup_key (Optional[str]): name of the startup key file.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError('Missing parent value.')

    super(BDEPathSpec, self).__init__(parent=parent, **kwargs)
    self.password = password
    self.recovery_password = recovery_password
    self.startup_key = startup_key

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    string_parts = []

    if self.password:
      string_parts.append(f'password: {self.password:s}')
    if self.recovery_password:
      string_parts.append(f'recovery_password: {self.recovery_password:s}')
    if self.startup_key:
      string_parts.append(f'startup_key: {self.startup_key:s}')

    return self._GetComparable(sub_comparable_string=', '.join(string_parts))


factory.Factory.RegisterPathSpec(BDEPathSpec)
