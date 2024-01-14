# -*- coding: utf-8 -*-
"""The RC4 decrypter implementation."""

import pyfcrypto

from dfvfs.encryption import decrypter
from dfvfs.encryption import manager
from dfvfs.lib import definitions


class RC4Decrypter(decrypter.Decrypter):
  """RC4 decrypter using Cryptography."""

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

    super(RC4Decrypter, self).__init__(**kwargs)
    self._rc4_context = pyfcrypto.rc4_context()

    self._rc4_context.set_key(key)

  # pylint: disable=unused-argument
  def Decrypt(self, encrypted_data, finalize=False):
    """Decrypts the encrypted data.

    Args:
      encrypted_data (bytes): encrypted data.
      finalize (Optional[bool]): True if the end of data has been reached and
          the cipher context should be finalized.

    Returns:
      tuple[bytes,bytes]: decrypted data and remaining encrypted data.
    """
    decrypted_data = pyfcrypto.crypt_rc4(self._rc4_context, encrypted_data)
    return decrypted_data, b''


manager.EncryptionManager.RegisterDecrypter(RC4Decrypter)
