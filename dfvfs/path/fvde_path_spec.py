# -*- coding: utf-8 -*-
"""The FileVault Drive Encryption (FVDE) path specification implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class FVDEPathSpec(path_spec.PathSpec):
  """FVDE path specification.

  Attributes:
    encrypted_root_plist (str): path to the EncryptedRoot.plist.wipekey file.
    password (str): password.
    recovery_password (str): recovery password.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FVDE

  def __init__(
      self, encrypted_root_plist=None, password=None, parent=None,
      recovery_password=None, **kwargs):
    """Initializes a path specification.

    Note that the FVDE path specification must have a parent.

    Args:
      encrypted_root_plist (Optional[str]): path to the
          EncryptedRoot.plist.wipekey file.
      password (Optional[str]): password.
      parent (Optional[PathSpec]): parent path specification.
      recovery_password (Optional[str]): recovery password.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError('Missing parent value.')

    super(FVDEPathSpec, self).__init__(parent=parent, **kwargs)
    self.encrypted_root_plist = encrypted_root_plist
    self.password = password
    self.recovery_password = recovery_password

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    string_parts = []

    if self.encrypted_root_plist:
      string_parts.append('encrypted_root_plist: {0:s}'.format(
          self.encrypted_root_plist))
    if self.password:
      string_parts.append('password: {0:s}'.format(self.password))
    if self.recovery_password:
      string_parts.append('recovery_password: {0:s}'.format(
          self.recovery_password))

    return self._GetComparable(sub_comparable_string=', '.join(string_parts))


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(FVDEPathSpec)
