# -*- coding: utf-8 -*-
"""The AES decrypter implementation."""

from __future__ import unicode_literals

from cryptography.hazmat.primitives.ciphers import algorithms

from dfvfs.encryption import decrypter
from dfvfs.encryption import manager
from dfvfs.lib import definitions


class AESDecrypter(decrypter.CryptographyBlockCipherDecrypter):
  """AES decrypter using Cryptography."""

  ENCRYPTION_METHOD = definitions.ENCRYPTION_METHOD_AES

  _ENCRYPTION_MODES = frozenset([
      definitions.ENCRYPTION_MODE_CBC,
      definitions.ENCRYPTION_MODE_CFB,
      definitions.ENCRYPTION_MODE_ECB,
      definitions.ENCRYPTION_MODE_OFB])

  def __init__(
      self, cipher_mode=None, initialization_vector=None, key=None, **kwargs):
    """Initializes a decrypter.

    Args:
      cipher_mode (Optional[str]): cipher mode.
      initialization_vector (Optional[bytes]): initialization vector.
      key (Optional[bytes]): key.
      kwargs (dict): keyword arguments depending on the decrypter.

    Raises:
      ValueError: when key is not set or the cipher mode is not supported.
    """
    if not key:
      raise ValueError('Missing key.')

    if cipher_mode not in self._ENCRYPTION_MODES:
      raise ValueError('Unsupported cipher mode: {0!s}'.format(cipher_mode))

    algorithm = algorithms.AES(key)

    super(AESDecrypter, self).__init__(
        algorithm=algorithm, cipher_mode=cipher_mode,
        initialization_vector=initialization_vector, **kwargs)


manager.EncryptionManager.RegisterDecrypter(AESDecrypter)
