# -*- coding: utf-8 -*-
"""Helper function for FileVault Drive Encryption (FVDE) support."""


def FVDEVolumeOpen(fvde_volume, path_spec, file_object, key_chain):
  """Opens the FVDE volume using the path specification.

  Args:
    fvde_volume (pyfvde.volume): FVDE volume.
    path_spec (PathSpec): path specification.
    file_object (FileIO): file-like object.
    key_chain (KeyChain): key chain.
  """
  password = key_chain.GetCredential(path_spec, u'password')
  if password:
    fvde_volume.set_password(password)

  recovery_password = key_chain.GetCredential(path_spec, u'recovery_password')
  if recovery_password:
    fvde_volume.set_recovery_password(recovery_password)

  fvde_volume.open_file_object(file_object)
