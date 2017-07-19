# -*- coding: utf-8 -*-
"""The RC4 decrypter implementation."""

from __future__ import unicode_literals

from Crypto.Cipher import ARC4

from dfvfs.encryption import decrypter
from dfvfs.encryption import manager
from dfvfs.lib import definitions


class RC4Decrypter(decrypter.Decrypter):
  """RC4 decrypter using pycrypto."""

  ENCRYPTION_METHOD = definitions.ENCRYPTION_METHOD_RC4

  def __init__(self, key=None, **kwargs):
    """Initializes a decrypter.

    Args:
      key (Optional[bytes]): key.
      kwargs (dict): keyword arguments depending on the decrypter.

    Raises:
      ValueError: when key is not set.
    """
    if not key:
      raise ValueError('Missing key.')

    super(RC4Decrypter, self).__init__()
    self._rc4_cipher = ARC4.new(key)

  def Decrypt(self, encrypted_data):
    """Decrypts the encrypted data.

    Args:
      encrypted_data (bytes): encrypted data.

    Returns:
      tuple[bytes,bytes]: decrypted data and remaining encrypted data.
    """
    decrypted_data = self._rc4_cipher.decrypt(encrypted_data)
    return decrypted_data, b''


manager.EncryptionManager.RegisterDecrypter(RC4Decrypter)
