# -*- coding: utf-8 -*-
"""The encrypted stream path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class EncryptedStreamPathSpec(path_spec.PathSpec):
  """Class that implements the encrypted stream path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ENCRYPTED_STREAM

  def __init__(self, encryption_method=None, parent=None, **kwargs):
    """Initializes the path specification object.

    Note that the encrypted stream path specification must have a parent.

    Args:
      encryption_method: optional method used to the encrypt the data.
      parent: optional parent path specification (instance of PathSpec).
      kwargs: a dictionary of keyword arguments depending on the path
              specification.

    Raises:
      ValueError: when encryption method or parent are not set.
    """
    if not encryption_method or not parent:
      raise ValueError(u'Missing encryption method or parent value.')

    super(EncryptedStreamPathSpec, self).__init__(parent=parent, **kwargs)
    self.encryption_method = encryption_method

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    sub_comparable_string = (
        u'encryption_method: {0:s}').format(self.encryption_method)
    return self._GetComparable(sub_comparable_string=sub_comparable_string)


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(EncryptedStreamPathSpec)
