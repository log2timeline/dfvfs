# -*- coding: utf-8 -*-
"""Helper functions for Volume Shadow Snapshots (VSS) support."""


def VShadowPathSpecGetStoreIndex(path_spec):
  """Retrieves the store index from the path specification.

  Args:
    path_spec: the path specification (instance of PathSpec).
  """
  store_index = getattr(path_spec, u'store_index', None)

  if store_index is None:
    location = getattr(path_spec, u'location', None)

    if location is None or not location.startswith(u'/vss'):
      return

    store_index = None
    try:
      store_index = int(location[4:], 10) - 1
    except ValueError:
      pass

    if store_index is None or store_index < 0:
      return

  return store_index
