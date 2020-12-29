# -*- coding: utf-8 -*-
"""The fake path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import location_path_spec


class FakePathSpec(location_path_spec.LocationPathSpec):
  """Fake path specification."""

  _IS_SYSTEM_LEVEL = True
  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FAKE

  def __init__(self, location=None, **kwargs):
    """Initializes a path specification.

    Note that the fake path specification cannot have a parent.

    Args:
      location (Optional[str]): location e.g. /opt/dfvfs.

    Raises:
      ValueError: when parent is set.
    """
    parent = None
    if 'parent' in kwargs:
      parent = kwargs['parent']
      del kwargs['parent']

    if parent:
      raise ValueError('Parent value set.')

    super(FakePathSpec, self).__init__(
        location=location, parent=parent, **kwargs)


factory.Factory.RegisterPathSpec(FakePathSpec)
