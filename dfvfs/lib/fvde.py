# -*- coding: utf-8 -*-
"""Helper function for FileVault Drive Encryption (FVDE) support."""

from __future__ import unicode_literals


def FVDEVolumeOpen(fvde_volume, path_spec, file_object, key_chain):
  """Opens the FVDE volume using the path specification.

  Args:
    fvde_volume (pyfvde.volume): FVDE volume.
    path_spec (PathSpec): path specification.
    file_object (FileIO): file-like object.
    key_chain (KeyChain): key chain.
  """
  encrypted_root_plist = key_chain.GetCredential(
      path_spec, 'encrypted_root_plist')
  if encrypted_root_plist:
    fvde_volume.read_encrypted_root_plist(encrypted_root_plist)

  password = key_chain.GetCredential(path_spec, 'password')
  if password:
    fvde_volume.set_password(password)

  recovery_password = key_chain.GetCredential(path_spec, 'recovery_password')
  if recovery_password:
    fvde_volume.set_recovery_password(recovery_password)

  fvde_volume.open_file_object(file_object)
