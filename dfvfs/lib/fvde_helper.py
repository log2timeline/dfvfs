# -*- coding: utf-8 -*-
"""Helper function for FileVault Drive Encryption (FVDE) support."""


def FVDEOpenVolume(fvde_volume, path_spec, file_object, key_chain):
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


def FVDEUnlockVolume(fvde_volume, path_spec, key_chain):
  """Unlocks a FVDE volume using the path specification.

  Args:
    fvde_volume (pyfvde.volume): FVDE volume.
    path_spec (PathSpec): path specification.
    key_chain (KeyChain): key chain.

  Returns:
    bool: True if the volume is unlocked, False otherwise.
  """
  is_locked = fvde_volume.is_locked()
  if is_locked:
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

    is_locked = not fvde_volume.unlock()

  return not is_locked
