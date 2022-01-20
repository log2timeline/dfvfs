# -*- coding: utf-8 -*-
"""Helper functions for Logical Volume Manager (LVM) support."""


_LVM_LOCATION_PREFIX = '/lvm'
_LVM_LOCATION_PREFIX_LENGTH = len(_LVM_LOCATION_PREFIX)


def LVMPathSpecGetVolumeIndex(path_spec):
  """Retrieves the volume index from the path specification.

  Args:
    path_spec (PathSpec): path specification.

  Returns:
    int: volume index or None if not available.
  """
  volume_index = getattr(path_spec, 'volume_index', None)

  if volume_index is None:
    location = getattr(path_spec, 'location', None)

    if location is None or not location.startswith(_LVM_LOCATION_PREFIX):
      return None

    volume_index = None
    try:
      volume_index = int(location[_LVM_LOCATION_PREFIX_LENGTH:], 10) - 1
    except ValueError:
      pass

    if volume_index is None or volume_index < 0:
      return None

  return volume_index
