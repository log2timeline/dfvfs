# -*- coding: utf-8 -*-
"""Helper functions for Apple File System (APFS) support."""


def APFSUnlockVolume(fsapfs_volume, path_spec, key_chain):
  """Unlocks an APFS volume using the path specification.

  Args:
    fsapfs_volume (pyapfs.volume): APFS volume.
    path_spec (PathSpec): path specification.
    key_chain (KeyChain): key chain.

  Returns:
    bool: True if the volume is unlocked, False otherwise.
  """
  is_locked = fsapfs_volume.is_locked()
  if is_locked:
    password = key_chain.GetCredential(path_spec, 'password')
    if password:
      fsapfs_volume.set_password(password)

    recovery_password = key_chain.GetCredential(path_spec, 'recovery_password')
    if recovery_password:
      fsapfs_volume.set_recovery_password(recovery_password)

    is_locked = not fsapfs_volume.unlock()

  return not is_locked
