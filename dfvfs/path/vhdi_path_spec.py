# -*- coding: utf-8 -*-
"""The VHD image path specification implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class VHDIPathSpec(path_spec.PathSpec):
  """VHD image path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VHDI

  def __init__(self, parent=None, **kwargs):
    """Initializes a path specification.

    Note that the VHDI file path specification must have a parent.

    Args:
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError('Missing parent value.')

    super(VHDIPathSpec, self).__init__(parent=parent, **kwargs)


factory.Factory.RegisterPathSpec(VHDIPathSpec)
