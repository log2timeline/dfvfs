# -*- coding: utf-8 -*-
"""The decrypter object interface."""

import abc


class Decrypter(object):
  """Class that implements the decrypter object interface."""

  def __init__(self, **kwargs):
    """Initializes the decrypter object.

    Args:
      kwargs (dict): keyword arguments depending on the decrypter.

    Raises:
      ValueError: when there are unused keyword arguments.
    """
    if kwargs:
      raise ValueError(u'Unused keyword arguments: {0:s}.'.format(
          u', '.join(kwargs)))

    super(Decrypter, self).__init__()

  @abc.abstractmethod
  def Decrypt(self, encrypted_data):
    """Decrypts the encrypted data.

    Args:
      encrypted_data (bytes): encrypted data.

    Returns:
      tuple[bytes,bytes]: decrypted data and remaining encrypted data.
    """
