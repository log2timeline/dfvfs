# -*- coding: utf-8 -*-
"""The decrypter interface."""

import abc

from cryptography.hazmat import backends
from cryptography.hazmat.primitives import ciphers
from cryptography.hazmat.primitives.ciphers import modes

from dfvfs.lib import definitions
from dfvfs.lib import errors


class Decrypter(object):
  """Decrypter interface."""

  def __init__(self, **kwargs):
    """Initializes a decrypter.

    Args:
      kwargs (dict): keyword arguments depending on the decrypter.

    Raises:
      ValueError: when there are unused keyword arguments.
    """
    if kwargs:
      keyword_arguments = ', '.join(kwargs)
      raise ValueError(f'Unused keyword arguments: {keyword_arguments:s}.')

    super(Decrypter, self).__init__()

  # pylint: disable=redundant-returns-doc
  @abc.abstractmethod
  def Decrypt(self, encrypted_data, finalize=False):
    """Decrypts the encrypted data.

    Args:
      encrypted_data (bytes): encrypted data.
      finalize (Optional[bool]): True if the end of data has been reached and
          the cipher context should be finalized.

    Returns:
      tuple[bytes, bytes]: decrypted data and remaining encrypted data.
    """


class CryptographyBlockCipherDecrypter(Decrypter):
  """Block cipher decrypter using Cryptography."""

  def __init__(
      self, algorithm=None, cipher_mode=None, initialization_vector=None,
      **kwargs):
    """Initializes a decrypter.

    Args:
      algorithm (Optional[Cryptography.CipherAlgorithm]): cipher algorithm.
      cipher_mode (Optional[str]): cipher mode.
      initialization_vector (Optional[bytes]): initialization vector.
      kwargs (dict): keyword arguments depending on the decrypter.

    Raises:
      BackEndError: when the cryptography backend cannot be initialized.
      ValueError: if the initialization_vector is required and not set.
    """
    if (cipher_mode != definitions.ENCRYPTION_MODE_ECB and
        not initialization_vector):
      raise ValueError('Missing initialization vector.')

    if cipher_mode == definitions.ENCRYPTION_MODE_CBC:
      mode = modes.CBC(initialization_vector)
    elif cipher_mode == definitions.ENCRYPTION_MODE_CFB:
      mode = modes.CFB(initialization_vector)
    elif cipher_mode == definitions.ENCRYPTION_MODE_ECB:
      mode = modes.ECB()
    elif cipher_mode == definitions.ENCRYPTION_MODE_OFB:
      mode = modes.OFB(initialization_vector)

    try:
      backend = backends.default_backend()
    except ImportError as exception:
      raise errors.BackEndError(exception)

    cipher = ciphers.Cipher(algorithm, mode=mode, backend=backend)

    super(CryptographyBlockCipherDecrypter, self).__init__()
    self._algorithm = algorithm
    self._cipher_context = cipher.decryptor()

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

    _, block_offset = divmod(encrypted_data_size, self._algorithm.block_size)

    remaining_encrypted_data = b''
    if not finalize and block_offset > 0:
      remaining_encrypted_data = encrypted_data[-block_offset:]
      encrypted_data = encrypted_data[:-block_offset]

    decrypted_data = self._cipher_context.update(encrypted_data)

    if finalize:
      if block_offset > 0:
        block_padding_size = self._algorithm.block_size - block_offset
        block_padding = b'\x00' * block_padding_size

        decrypted_data += self._cipher_context.update(block_padding)

      decrypted_data += self._cipher_context.finalize()
      decrypted_data = decrypted_data[:encrypted_data_size]

    return decrypted_data, remaining_encrypted_data
