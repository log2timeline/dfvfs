# -*- coding: utf-8 -*-
"""The Blowfish decrypter object implementation."""

from Crypto.Cipher import Blowfish

from dfvfs.encryption import decrypter
from dfvfs.encryption import manager
from dfvfs.lib import definitions


class BlowfishDecrypter(decrypter.Decrypter):
  """Class that implements a Blowfish decrypter using pycrypto."""

  ENCRYPTION_METHOD = definitions.ENCRYPTION_METHOD_BLOWFISH

  ENCRYPTION_MODES = {
      definitions.ENCRYPTION_MODE_CBC : Blowfish.MODE_CBC,
      definitions.ENCRYPTION_MODE_CFB : Blowfish.MODE_CFB,
      definitions.ENCRYPTION_MODE_ECB : Blowfish.MODE_ECB,
      definitions.ENCRYPTION_MODE_OFB : Blowfish.MODE_OFB}

  def __init__(self, key=None, mode=None, initialization_vector=None, **kwargs):
    """Initializes the decrypter object.

    Args:
      key: optional binary string containing the key.
      mode: optional mode of operation.
      initialization_vector: optional initialization vector.
      kwargs: a dictionary of keyword arguments depending on the decrypter.

    Raises:
      ValueError: when key is not set, block cipher mode is not supported,
                  when initialization_vector is required and not set.
    """
    if not key:
      raise ValueError(u'Missing key.')

    if mode not in self.ENCRYPTION_MODES:
      raise ValueError(u'Unsupported mode of operation: {0!s}'.format(mode))

    mode = self.ENCRYPTION_MODES[mode]

    super(BlowfishDecrypter, self).__init__()
    if mode == Blowfish.MODE_ECB:
      self._blowfish_cipher = Blowfish.new(key, mode=mode)
    elif initialization_vector:
      self._blowfish_cipher = Blowfish.new(
          key, mode=mode, IV=initialization_vector)
    else:
      # Pycrypto does not create a meaningful error when initialization vector
      # is missing. Therefore, we report it ourselves.
      raise ValueError(u'Missing initialization vector.')

  def Decrypt(self, encrypted_data):
    """Decrypts the encrypted data.

    Args:
      encrypted_data: a byte string containing the encrypted data.

    Returns:
      A tuple containing a byte string of the decrypted data and
      the remaining encrypted data.
    """
    index_split = -(len(encrypted_data) % Blowfish.block_size)
    if index_split:
      remaining_encrypted_data = encrypted_data[index_split:]
      encrypted_data = encrypted_data[:index_split]
    else:
      remaining_encrypted_data = b''

    decrypted_data = self._blowfish_cipher.decrypt(encrypted_data)

    return decrypted_data, remaining_encrypted_data


manager.EncryptionManager.RegisterDecrypter(BlowfishDecrypter)
