# -*- coding: utf-8 -*-
"""The decrypter interface."""

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
      keyword_arguments = ', '.join(kwargs)
      raise ValueError(f'Unused keyword arguments: {keyword_arguments:s}.')

    super(Decrypter, self).__init__()

  # pylint: disable=redundant-returns-doc
  @abc.abstractmethod
  def Decrypt(self, encrypted_data, finalize=False):
    """Decrypts the encrypted data.

    Args:
      encrypted_data (bytes): encrypted data.
      finalize (Optional[bool]): True if the end of data has been reached and
          the cipher context should be finalized.

    Returns:
      tuple[bytes, bytes]: decrypted data and remaining encrypted data.
    """
