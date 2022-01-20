# -*- coding: utf-8 -*-
"""Helper function for Core Storage (CS) support."""


_CS_LOCATION_PREFIX = '/cs'
_CS_LOCATION_PREFIX_LENGTH = len(_CS_LOCATION_PREFIX)


def CSPathSpecGetVolumeIndex(path_spec):
  """Retrieves the volume index from the path specification.

  Args:
    path_spec (PathSpec): path specification.

  Returns:
    int: volume index or None if not available.
  """
  volume_index = getattr(path_spec, 'volume_index', None)

  if volume_index is None:
    location = getattr(path_spec, 'location', None)

    if location is None or not location.startswith(_CS_LOCATION_PREFIX):
      return None

    volume_index = None
    try:
      volume_index = int(location[_CS_LOCATION_PREFIX_LENGTH:], 10) - 1
    except ValueError:
      pass

    if volume_index is None or volume_index < 0:
      return None

  return volume_index


def CSUnlockLogicalVolume(fvde_logical_volume, path_spec, key_chain):
  """Unlocks a Core Storage logical volume using the path specification.

  Args:
    fvde_logical_volume (pyfvde.logical_volume): Core Storage logical volume.
    path_spec (PathSpec): path specification.
    key_chain (KeyChain): key chain.

  Returns:
    bool: True if the volume is unlocked, False otherwise.
  """
  is_locked = fvde_logical_volume.is_locked()
  if is_locked:
    password = key_chain.GetCredential(path_spec, 'password')
    if password:
      fvde_logical_volume.set_password(password)

    recovery_password = key_chain.GetCredential(path_spec, 'recovery_password')
    if recovery_password:
      fvde_logical_volume.set_recovery_password(recovery_password)

    is_locked = not fvde_logical_volume.unlock()

  return not is_locked
