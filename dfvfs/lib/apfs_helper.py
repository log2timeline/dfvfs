# -*- coding: utf-8 -*-
"""Helper functions for Apple File System (APFS) support."""

from __future__ import unicode_literals


def APFSContainerPathSpecGetVolumeIndex(path_spec):
  """Retrieves the volume index from the path specification.

  Args:
    path_spec (PathSpec): path specification.

  Returns:
    int: volume index or None if the index cannot be determined.
  """
  volume_index = getattr(path_spec, 'volume_index', None)
  if volume_index is not None:
    return volume_index

  location = getattr(path_spec, 'location', None)
  if location is None or not location.startswith('/apfs'):
    return None

  try:
    volume_index = int(location[5:], 10) - 1
  except (TypeError, ValueError):
    volume_index = None

  if volume_index is None or volume_index < 0 or volume_index > 99:
    volume_index = None

  return volume_index


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
