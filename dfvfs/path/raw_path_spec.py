# -*- coding: utf-8 -*-
"""The RAW storage media image path specification implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class RawPathSpec(path_spec.PathSpec):
  """RAW storage media image path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_RAW

  def __init__(self, parent=None, **kwargs):
    """Initializes a path specification.

    Note that the RAW path specification must have a parent.

    Args:
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError('Missing parent value.')

    super(RawPathSpec, self).__init__(parent=parent, **kwargs)


factory.Factory.RegisterPathSpec(RawPathSpec)
