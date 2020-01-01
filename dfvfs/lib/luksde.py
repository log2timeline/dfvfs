# -*- coding: utf-8 -*-
"""Helper function for LUKS Drive Encryption support."""

from __future__ import unicode_literals


def LUKSDEVolumeOpen(luksde_volume, path_spec, file_object, key_chain):
  """Opens the LUKSDE volume using the path specification.

  Args:
    luksde_volume (pyluksde.volume): LUKSDE volume.
    path_spec (PathSpec): path specification.
    file_object (FileIO): file-like object.
    key_chain (KeyChain): key chain.
  """
  password = key_chain.GetCredential(path_spec, 'password')
  if password:
    luksde_volume.set_password(password)

  luksde_volume.open_file_object(file_object)
