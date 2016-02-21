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
      initialization_vector: optional initialization vector. (defaults to 0)
      kwargs: a dictionary of keyword arguments depending on the decrypter.

    Raises:
      ValueError: when key is not set or, the key or initialization vector size
                  is not supported.
    """
    if not key:
      raise ValueError(u'Missing key.')

    if len(key) not in AES.key_size:
      raise ValueError(u'Unsupported key size.')

    if initialization_vector is not None:
      if len(initialization_vector) != AES.block_size:
        raise ValueError(u'Unsupported initialization vector size.')
    else:
      initialization_vector = 0

    if not mode:
      raise ValueError(u'Missing mode of operation.')

    if mode not in self.ENCRYPTION_MODES:
      raise ValueError(u'Unsupported mode of operation: {0:s}'.format(mode))

    mode = self.ENCRYPTION_MODES[mode]

    super(AESDecrypter, self).__init__()
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
