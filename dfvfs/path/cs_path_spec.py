# -*- coding: utf-8 -*-
"""The Core Storage (CS) path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class CSPathSpec(path_spec.PathSpec):
  """CS path specification.

  Attributes:
    encrypted_root_plist (str): path to the EncryptedRoot.plist.wipekey file.
    location (str): location.
    password (str): password.
    recovery_password (str): recovery password.
    volume_index (int): logical volume index.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_CS

  def __init__(
      self, encrypted_root_plist=None, location=None, password=None,
      parent=None, recovery_password=None, volume_index=None, **kwargs):
    """Initializes a path specification.

    Note that the CS path specification must have a parent.

    Args:
      encrypted_root_plist (Optional[str]): path to the
          EncryptedRoot.plist.wipekey file.
      location (Optional[str]): location.
      password (Optional[str]): password.
      parent (Optional[PathSpec]): parent path specification.
      recovery_password (Optional[str]): recovery password.
      volume_index (Optional[int]): logical volume index.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError('Missing parent value.')

    super(CSPathSpec, self).__init__(parent=parent, **kwargs)
    self.encrypted_root_plist = encrypted_root_plist
    self.location = location
    self.password = password
    self.recovery_password = recovery_password
    self.volume_index = volume_index

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    string_parts = []

    if self.encrypted_root_plist:
      string_parts.append(
          f'encrypted_root_plist: {self.encrypted_root_plist:s}')
    if self.location is not None:
      string_parts.append(f'location: {self.location:s}')
    if self.password:
      string_parts.append(f'password: {self.password:s}')
    if self.recovery_password:
      string_parts.append(f'recovery_password: {self.recovery_password:s}')
    if self.volume_index is not None:
      string_parts.append(f'volume index: {self.volume_index:d}')

    return self._GetComparable(sub_comparable_string=', '.join(string_parts))


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(CSPathSpec)
