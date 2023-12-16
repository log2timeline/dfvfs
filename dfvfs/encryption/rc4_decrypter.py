# -*- coding: utf-8 -*-
"""The RC4 decrypter implementation."""

from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat import backends
from cryptography.hazmat.primitives import ciphers

from dfvfs.encryption import decrypter
from dfvfs.encryption import manager
from dfvfs.lib import definitions
from dfvfs.lib import errors


class RC4Decrypter(decrypter.Decrypter):
  """RC4 decrypter using Cryptography."""

  ENCRYPTION_METHOD = definitions.ENCRYPTION_METHOD_RC4

  def __init__(self, key=None, **kwargs):
    """Initializes a decrypter.

    Args:
      key (Optional[bytes]): key.
      kwargs (dict): keyword arguments depending on the decrypter.

    Raises:
      BackEndError: when the cryptography backend cannot be initialized.
      ValueError: when key is not set.
    """
    if not key:
      raise ValueError('Missing key.')

    algorithm = algorithms.ARC4(key)

    try:
      backend = backends.default_backend()
    except ImportError as exception:
      raise errors.BackEndError(exception)

    cipher = ciphers.Cipher(algorithm, mode=None, backend=backend)

    super(RC4Decrypter, self).__init__(**kwargs)
    self._cipher_context = cipher.decryptor()

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
    decrypted_data = self._cipher_context.update(encrypted_data)
    return decrypted_data, b''


manager.EncryptionManager.RegisterDecrypter(RC4Decrypter)
