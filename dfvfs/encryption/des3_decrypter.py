# -*- coding: utf-8 -*-
"""The triple DES decrypter implementation."""

import pyfcrypto

from dfvfs.encryption import decrypter
from dfvfs.encryption import manager
from dfvfs.lib import definitions


class DES3Decrypter(decrypter.Decrypter):
  """Triple DES decrypter using pyfcrypto."""

  ENCRYPTION_METHOD = definitions.ENCRYPTION_METHOD_DES3

  _BLOCK_SIZE = 8

  # TODO: add CFB and OFB support

  _ENCRYPTION_MODES = frozenset([
      definitions.ENCRYPTION_MODE_CBC,
      definitions.ENCRYPTION_MODE_ECB])

  def __init__(
      self, cipher_mode=None, initialization_vector=None, key=None, **kwargs):
    """Initializes a decrypter.

    Args:
      cipher_mode (Optional[str]): cipher mode.
      initialization_vector (Optional[bytes]): initialization vector.
      key (Optional[bytes]): key.
      kwargs (dict): keyword arguments depending on the decrypter.

    Raises:
      ValueError: when key is not set, the cipher mode is not supported or
          initialization vector not set or not supported.
      TypeError: when the initialization vector type is not supported.
    """
    if not key:
      raise ValueError('Missing key.')

    if cipher_mode not in self._ENCRYPTION_MODES:
      raise ValueError(f'Unsupported cipher mode: {cipher_mode!s}')

    if (cipher_mode != definitions.ENCRYPTION_MODE_ECB and
        not initialization_vector):
      raise ValueError('Missing initialization vector.')

    if initialization_vector and not isinstance(initialization_vector, bytes):
      raise TypeError('Unsupported initialization vector type.')

    if initialization_vector and len(initialization_vector) != self._BLOCK_SIZE:
      raise ValueError('Unsupported initialization vector size.')

    super(DES3Decrypter, self).__init__()
    self._des3_context = pyfcrypto.des3_context()
    self._cipher_mode = cipher_mode
    self._initialization_vector = initialization_vector

    self._des3_context.set_key(key)

  def Decrypt(self, encrypted_data, finalize=False):
    """Decrypts the encrypted data.

    Args:
      encrypted_data (bytes): encrypted data.
      finalize (Optional[bool]): True if the end of data has been reached and
          the cipher context should be finalized.

    Returns:
      tuple[bytes, bytes]: decrypted data and remaining encrypted data.
    """
    encrypted_data_size = len(encrypted_data)

    _, block_offset = divmod(encrypted_data_size, self._BLOCK_SIZE)

    remaining_encrypted_data = b''
    if block_offset > 0:
      if finalize:
        block_padding_size = self._BLOCK_SIZE - block_offset
        encrypted_data = b''.join([
            encrypted_data, b'\x00' * block_padding_size])
      else:
        remaining_encrypted_data = encrypted_data[-block_offset:]
        encrypted_data = encrypted_data[:-block_offset]

    if self._cipher_mode == definitions.ENCRYPTION_MODE_CBC:
      decrypted_data = pyfcrypto.crypt_des3_cbc(
          self._des3_context, pyfcrypto.crypt_modes.DECRYPT,
          self._initialization_vector, encrypted_data)

      self._initialization_vector = encrypted_data[-self._BLOCK_SIZE:]

    elif self._cipher_mode == definitions.ENCRYPTION_MODE_ECB:
      decrypted_data = pyfcrypto.crypt_des3_ecb(
          self._des3_context, pyfcrypto.crypt_modes.DECRYPT,
          encrypted_data)

    decrypted_data_size = encrypted_data_size - block_offset
    return decrypted_data[:decrypted_data_size], remaining_encrypted_data


manager.EncryptionManager.RegisterDecrypter(DES3Decrypter)
