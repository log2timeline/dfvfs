# -*- coding: utf-8 -*-
"""Helper functions for Logical Volume Manager (LVM) support."""


def LVMPathSpecGetVolumeIndex(path_spec):
  """Retrieves the volume index from the path specification.

  Args:
    path_spec: the path specification (instance of PathSpec).
  """
  volume_index = getattr(path_spec, u'volume_index', None)

  if volume_index is None:
    location = getattr(path_spec, u'location', None)

    if location is None or not location.startswith(u'/lvm'):
      return

    volume_index = None
    try:
      volume_index = int(location[4:], 10) - 1
    except ValueError:
      pass

    if volume_index is None or volume_index < 0:
      return

  return volume_index
