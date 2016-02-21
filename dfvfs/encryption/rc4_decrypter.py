# -*- coding: utf-8 -*-
"""The RC4 decrypter object implementation."""

from Crypto.Cipher import ARC4

from dfvfs.encryption import decrypter
from dfvfs.encryption import manager
from dfvfs.lib import definitions


class RC4Decrypter(decrypter.Decrypter):
  """Class that implements a RC4 decrypter using pycrypto."""

  ENCRYPTION_METHOD = definitions.ENCRYPTION_METHOD_RC4

  def __init__(self, key=None, **kwargs):
    """Initializes the decrypter object.

    Args:
      key: optional binary string containing the key.
      kwargs: a dictionary of keyword arguments depending on the decrypter.

    Raises:
      ValueError: when key is not set.
    """
    if not key:
      raise ValueError(u'Missing key.')

    super(RC4Decrypter, self).__init__()
    self._rc4_cipher = ARC4.new(key)

  def Decrypt(self, encrypted_data):
    """Decrypts the encrypted data.

    Args:
      encrypted_data: a byte string containing the encrypted data.

    Returns:
      A tuple containing a byte string of the decrypted data and
      the remaining encrypted data.
    """
    decrypted_data = self._rc4_cipher.decrypt(encrypted_data)
    return decrypted_data, b''


manager.EncryptionManager.RegisterDecrypter(RC4Decrypter)
