# -*- coding: utf-8 -*-
"""Helper functions for Volume Shadow Snapshots (VSS) support."""


def VShadowPathSpecGetStoreIndex(path_spec):
  """Retrieves the store index from the path specification.

  Args:
    path_spec (PathSpec): path specification.

  Returns:
    int: store index or None if not available.
  """
  store_index = getattr(path_spec, 'store_index', None)

  if store_index is None:
    location = getattr(path_spec, 'location', None)

    if location is None or not location.startswith('/vss'):
      return None

    store_index = None
    try:
      store_index = int(location[4:], 10) - 1
    except (TypeError, ValueError):
      pass

    if store_index is None or store_index < 0:
      return None

  return store_index
