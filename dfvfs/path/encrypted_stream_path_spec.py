# -*- coding: utf-8 -*-
"""The encrypted stream path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class EncryptedStreamPathSpec(path_spec.PathSpec):
  """Class that implements the encrypted stream path specification.

  Attributes:
    cipher_mode (str): cipher mode.
    encryption_method (str): method used to the encrypt the data.
    initialization_vector (bytes):  initialization vector.
    key (bytes): key.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ENCRYPTED_STREAM

  def __init__(
      self, cipher_mode=None, encryption_method=None,
      initialization_vector=None, key=None, parent=None, **kwargs):
    """Initializes the path specification.

    Note that the encrypted stream path specification must have a parent.

    Args:
      cipher_mode (Optional[str]): cipher mode.
      encryption_method (Optional[str]): method used to the encrypt the data.
      initialization_vector (Optional[bytes]):  initialization vector.
      key (Optional[bytes]): key.
      parent (Optional[PathSpec]): parent path specification.

    Raises:
      ValueError: when encryption method or parent are not set.
    """
    if not encryption_method or not parent:
      raise ValueError(u'Missing encryption method or parent value.')

    super(EncryptedStreamPathSpec, self).__init__(parent=parent, **kwargs)
    self.cipher_mode = cipher_mode
    self.encryption_method = encryption_method
    self.initialization_vector = initialization_vector
    self.key = key

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    string_parts = []

    if self.cipher_mode:
      string_parts.append(u'cipher_mode: {0:s}'.format(self.cipher_mode))
    if self.encryption_method:
      string_parts.append(u'encryption_method: {0:s}'.format(
          self.encryption_method))
    if self.initialization_vector:
      string_parts.append(u'initialization_vector: {0:s}'.format(
          self.initialization_vector.encode(u'hex')))
    if self.key:
      string_parts.append(u'key: {0:s}'.format(self.key.encode(u'hex')))

    return self._GetComparable(sub_comparable_string=u', '.join(string_parts))


factory.Factory.RegisterPathSpec(EncryptedStreamPathSpec)
