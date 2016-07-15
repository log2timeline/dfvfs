# -*- coding: utf-8 -*-
"""The triple DES decrypter object implementation."""

from Crypto.Cipher import DES3

from dfvfs.encryption import decrypter
from dfvfs.encryption import manager
from dfvfs.lib import definitions


class DES3Decrypter(decrypter.Decrypter):
  """Class that implements a triple DES decrypter using pycrypto."""

  ENCRYPTION_METHOD = definitions.ENCRYPTION_METHOD_DES3

  ENCRYPTION_MODES = {
      definitions.ENCRYPTION_MODE_CBC : DES3.MODE_CBC,
      definitions.ENCRYPTION_MODE_CFB : DES3.MODE_CFB,
      definitions.ENCRYPTION_MODE_ECB : DES3.MODE_ECB,
      definitions.ENCRYPTION_MODE_OFB : DES3.MODE_OFB}

  def __init__(self, key=None, mode=None, initialization_vector=None, **kwargs):
    """Initializes the decrypter object.

    Args:
      key (Optional[bytes]): key.
      mode (Optional[str]): mode of operation.
      initialization_vector (Optional[bytes]): initialization vector.
      kwargs (dict): keyword arguments depending on the decrypter.

    Raises:
      ValueError: when key is not set, block cipher mode is not supported,
                  or initialization_vector is required and not set.
    """
    if not key:
      raise ValueError(u'Missing key.')

    if mode not in self.ENCRYPTION_MODES:
      raise ValueError(u'Unsupported mode of operation: {0!s}'.format(mode))

    mode = self.ENCRYPTION_MODES[mode]

    if mode != DES3.MODE_ECB and not initialization_vector:
      # Pycrypto does not create a meaningful error when initialization vector
      # is missing. Therefore, we report it ourselves.
      raise ValueError(u'Missing initialization vector.')

    super(DES3Decrypter, self).__init__()
    if mode == DES3.MODE_ECB:
      self._des3_cipher = DES3.new(key, mode=mode)
    else:
      self._des3_cipher = DES3.new(key, mode=mode, IV=initialization_vector)

  def Decrypt(self, encrypted_data):
    """Decrypts the encrypted data.

    Args:
      encrypted_data (bytes): encrypted data.

    Returns:
      tuple[bytes,bytes]: decrypted data and remaining encrypted data.
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
