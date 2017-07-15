# -*- coding: utf-8 -*-
"""The compressed stream path specification implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class CompressedStreamPathSpec(path_spec.PathSpec):
  """Compressed stream path specification.

  Attributes:
    compression_method (str): method used to the compress the data.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_COMPRESSED_STREAM

  def __init__(self, compression_method=None, parent=None, **kwargs):
    """Initializes a path specification.

    Note that the compressed stream path specification must have a parent.

    Args:
      compression_method (Optional[str]): method used to the compress the data.
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when compression method or parent are not set.
    """
    if not compression_method or not parent:
      raise ValueError('Missing compression method or parent value.')

    super(CompressedStreamPathSpec, self).__init__(parent=parent, **kwargs)
    self.compression_method = compression_method

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    sub_comparable_string = (
        'compression_method: {0:s}').format(self.compression_method)
    return self._GetComparable(sub_comparable_string=sub_comparable_string)


factory.Factory.RegisterPathSpec(CompressedStreamPathSpec)
