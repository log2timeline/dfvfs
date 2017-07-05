# -*- coding: utf-8 -*-
"""The triple DES decrypter implementation."""

from __future__ import unicode_literals

from Crypto.Cipher import DES3

from dfvfs.encryption import decrypter
from dfvfs.encryption import manager
from dfvfs.lib import definitions


class DES3Decrypter(decrypter.Decrypter):
  """Triple DES decrypter using pycrypto."""

  ENCRYPTION_METHOD = definitions.ENCRYPTION_METHOD_DES3

  ENCRYPTION_MODES = {
      definitions.ENCRYPTION_MODE_CBC : DES3.MODE_CBC,
      definitions.ENCRYPTION_MODE_CFB : DES3.MODE_CFB,
      definitions.ENCRYPTION_MODE_ECB : DES3.MODE_ECB,
      definitions.ENCRYPTION_MODE_OFB : DES3.MODE_OFB}

  def __init__(
      self, cipher_mode=None, initialization_vector=None, key=None, **kwargs):
    """Initializes a decrypter.

    Args:
      cipher_mode (Optional[str]): cipher mode.
      initialization_vector (Optional[bytes]): initialization vector.
      key (Optional[bytes]): key.
      kwargs (dict): keyword arguments depending on the decrypter.

    Raises:
      ValueError: when key is not set, block cipher mode is not supported,
          or initialization_vector is required and not set.
    """
    if not key:
      raise ValueError('Missing key.')

    cipher_mode = self.ENCRYPTION_MODES.get(cipher_mode, None)
    if cipher_mode is None:
      raise ValueError('Unsupported cipher mode: {0!s}'.format(cipher_mode))

    if cipher_mode != DES3.MODE_ECB and not initialization_vector:
      # Pycrypto does not create a meaningful error when initialization vector
      # is missing. Therefore, we report it ourselves.
      raise ValueError('Missing initialization vector.')

    super(DES3Decrypter, self).__init__()
    if cipher_mode == DES3.MODE_ECB:
      self._des3_cipher = DES3.new(key, mode=cipher_mode)
    else:
      self._des3_cipher = DES3.new(
          key, IV=initialization_vector, mode=cipher_mode)

  def Decrypt(self, encrypted_data):
    """Decrypts the encrypted data.

    Args:
      encrypted_data (bytes): encrypted data.

    Returns:
      tuple[bytes, bytes]: decrypted data and remaining encrypted data.
    """
    index_split = -(len(encrypted_data) % DES3.block_size)
    if index_split:
      remaining_encrypted_data = encrypted_data[index_split:]
      encrypted_data = encrypted_data[:index_split]
    else:
      remaining_encrypted_data = b''

    decrypted_data = self._des3_cipher.decrypt(encrypted_data)

    return decrypted_data, remaining_encrypted_data


manager.EncryptionManager.RegisterDecrypter(DES3Decrypter)
