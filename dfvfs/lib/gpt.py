# -*- coding: utf-8 -*-
"""Helper functions for GUID Partition Table (GPT) support."""


def GPTPathSpecGetEntryIndex(path_spec):
  """Retrieves the entry index from the path specification.

  Args:
    path_spec (PathSpec): path specification.

  Returns:
    int: entry index or None if not available.
  """
  entry_index = getattr(path_spec, 'entry_index', None)

  if entry_index is None:
    location = getattr(path_spec, 'location', None)

    if location is None or not location.startswith('/p'):
      return None

    entry_index = None
    try:
      entry_index = int(location[2:], 10) - 1
    except ValueError:
      pass

    if entry_index is None or entry_index < 0:
      return None

  return entry_index
