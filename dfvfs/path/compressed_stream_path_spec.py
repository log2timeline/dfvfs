# -*- coding: utf-8 -*-
"""The compressed stream path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class CompressedStreamPathSpec(path_spec.PathSpec):
  """Class that implements the compressed stream path specification.

  Attributes:
    compression_method: string containing the method used to the compress
                        the data.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_COMPRESSED_STREAM

  def __init__(self, compression_method=None, parent=None, **kwargs):
    """Initializes the path specification object.

    Note that the compressed stream path specification must have a parent.

    Args:
      compression_method: optional string containing the method used to
                          the compress the data.
      parent: optional parent path specification (instance of PathSpec).
      kwargs: a dictionary of keyword arguments depending on the path
              specification.

    Raises:
      ValueError: when compression method or parent are not set.
    """
    if not compression_method or not parent:
      raise ValueError(u'Missing compression method or parent value.')

    super(CompressedStreamPathSpec, self).__init__(parent=parent, **kwargs)
    self.compression_method = compression_method

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    sub_comparable_string = (
        u'compression_method: {0:s}').format(self.compression_method)
    return self._GetComparable(sub_comparable_string=sub_comparable_string)


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(CompressedStreamPathSpec)
