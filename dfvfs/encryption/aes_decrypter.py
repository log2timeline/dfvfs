# -*- coding: utf-8 -*-
"""The AES decrypter object implementation."""

from Crypto.Cipher import AES

from dfvfs.encryption import decrypter
from dfvfs.encryption import manager
from dfvfs.lib import definitions


class AESDecrypter(decrypter.Decrypter):
  """Class that implements a AES decrypter using pycrypto."""

  ENCRYPTION_METHOD = definitions.ENCRYPTION_METHOD_AES

  ENCRYPTION_MODES = {
      definitions.ENCRYPTION_MODE_CBC : AES.MODE_CBC,
      definitions.ENCRYPTION_MODE_CFB : AES.MODE_CFB,
      definitions.ENCRYPTION_MODE_ECB : AES.MODE_ECB,
      definitions.ENCRYPTION_MODE_OFB : AES.MODE_OFB}

  def __init__(self, key=None, mode=None, initialization_vector=None, **kwargs):
    """Initializes the decrypter object.

    Args:
      key: optional binary string containing the key.
      mode: optional mode of operation.
      initialization_vector: optional initialization vector.
      kwargs: a dictionary of keyword arguments depending on the decrypter.

    Raises:
      ValueError: when key is not set, block cipher mode is not supported,
                  or initialization_vector is required and not set.
    """
    if not key:
      raise ValueError(u'Missing key.')

    if mode not in self.ENCRYPTION_MODES:
      raise ValueError(u'Unsupported mode of operation: {0!s}'.format(mode))

    mode = self.ENCRYPTION_MODES[mode]

    if mode != AES.MODE_ECB and not initialization_vector:
      # Pycrypto does not create a meaningful error when initialization vector
      # is missing. Therefore, we report it ourselves.
      raise ValueError(u'Missing initialization vector.')

    super(AESDecrypter, self).__init__()
    if mode == AES.MODE_ECB:
      self._aes_cipher = AES.new(key, mode=mode)
    else:
      self._aes_cipher = AES.new(key, mode=mode, IV=initialization_vector)

  def Decrypt(self, encrypted_data):
    """Decrypts the encrypted data.

    Args:
      encrypted_data: a byte string containing the encrypted data.

    Returns:
      A tuple containing a byte string of the decrypted data and
      the remaining encrypted data.
    """
    index_split = -(len(encrypted_data) % AES.block_size)
    if index_split:
      remaining_encrypted_data = encrypted_data[index_split:]
      encrypted_data = encrypted_data[:index_split]
    else:
      remaining_encrypted_data = b''

    decrypted_data = self._aes_cipher.decrypt(encrypted_data)

    return decrypted_data, remaining_encrypted_data


manager.EncryptionManager.RegisterDecrypter(AESDecrypter)
