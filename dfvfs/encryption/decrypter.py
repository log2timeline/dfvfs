# -*- coding: utf-8 -*-
"""The decrypter interface."""

from __future__ import unicode_literals

import abc


class Decrypter(object):
  """Decrypter interface."""

  def __init__(self, **kwargs):
    """Initializes a decrypter.

    Args:
      kwargs (dict): keyword arguments depending on the decrypter.

    Raises:
      ValueError: when there are unused keyword arguments.
    """
    if kwargs:
      raise ValueError('Unused keyword arguments: {0:s}.'.format(
          ', '.join(kwargs)))

    super(Decrypter, self).__init__()

  @abc.abstractmethod
  def Decrypt(self, encrypted_data):
    """Decrypts the encrypted data.

    Args:
      encrypted_data (bytes): encrypted data.

    Returns:
      tuple[bytes,bytes]: decrypted data and remaining encrypted data.
    """
