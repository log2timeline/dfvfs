# -*- coding: utf-8 -*-
"""The encoded stream path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class EncodedStreamPathSpec(path_spec.PathSpec):
  """Encoded stream path specification.

  Attributes:
    encoding_method (str): method used to the encode the data.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ENCODED_STREAM

  def __init__(self, encoding_method=None, parent=None, **kwargs):
    """Initializes a path specification.

    Note that the encoded stream path specification must have a parent.

    Args:
      encoding_method (Optional[str]): method used to the encode the data.
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when encoding method or parent are not set.
    """
    if not encoding_method or not parent:
      raise ValueError('Missing encoding method or parent value.')

    super(EncodedStreamPathSpec, self).__init__(parent=parent, **kwargs)
    self.encoding_method = encoding_method

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    return self._GetComparable(sub_comparable_string=(
        f'encoding_method: {self.encoding_method:s}'))


factory.Factory.RegisterPathSpec(EncodedStreamPathSpec)
