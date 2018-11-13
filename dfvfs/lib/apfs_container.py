# -*- coding: utf-8 -*-
"""Helper functions for APFS container support."""

from __future__ import unicode_literals


def APFSContainerPathSpecGetVolumeIndex(path_spec):
  """Retrieves the volume index from the path specification.

  Args:
    path_spec (PathSpec): path specification.

  Returns:
    int: volume index.
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
