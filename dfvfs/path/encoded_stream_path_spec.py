# -*- coding: utf-8 -*-
"""The encoded stream path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class EncodedStreamPathSpec(path_spec.PathSpec):
  """Class that implements the encoded stream path specification.

  Attributes:
    encoding_method: string containing the method used to the encode the data.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ENCODED_STREAM

  def __init__(self, encoding_method=None, parent=None, **kwargs):
    """Initializes the path specification object.

    Note that the encoded stream path specification must have a parent.

    Args:
      encoding_method: optional string containing the method used to the encode
                       the data.
      parent: optional parent path specification (instance of PathSpec).
      kwargs: a dictionary of keyword arguments depending on the path
              specification.

    Raises:
      ValueError: when encoding method or parent are not set.
    """
    if not encoding_method or not parent:
      raise ValueError(u'Missing encoding method or parent value.')

    super(EncodedStreamPathSpec, self).__init__(parent=parent, **kwargs)
    self.encoding_method = encoding_method

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    sub_comparable_string = (
        u'encoding_method: {0:s}').format(self.encoding_method)
    return self._GetComparable(sub_comparable_string=sub_comparable_string)


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(EncodedStreamPathSpec)
