# -*- coding: utf-8 -*-
"""Helper function for LUKS Drive Encryption support."""


def LUKSDEOpenVolume(luksde_volume, path_spec, file_object, key_chain):
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


def LUKSDEUnlockVolume(luksde_volume, path_spec, key_chain):
  """Unlocks a LUKSDE volume using the path specification.

  Args:
    luksde_volume (pyluksde.volume): LUKSDE volume.
    path_spec (PathSpec): path specification.
    key_chain (KeyChain): key chain.

  Returns:
    bool: True if the volume is unlocked, False otherwise.
  """
  is_locked = luksde_volume.is_locked()
  if is_locked:
    password = key_chain.GetCredential(path_spec, 'password')
    if password:
      luksde_volume.set_password(password)

    is_locked = not luksde_volume.unlock()

  return not is_locked
