# -*- coding: utf-8 -*-
"""The encryption manager."""


class EncryptionManager(object):
  """Encryption manager."""

  _decrypters = {}

  @classmethod
  def DeregisterDecrypter(cls, decrypter):
    """Deregisters a decrypter for a specific encryption method.

    Args:
      decrypter (type): decrypter class.

    Raises:
      KeyError: if the corresponding decrypter is not set.
    """
    encryption_method = decrypter.ENCRYPTION_METHOD.lower()
    if encryption_method not in cls._decrypters:
      raise KeyError((
          f'Decrypter for encryption method: {decrypter.ENCRYPTION_METHOD:s} '
          f'not set.'))

    del cls._decrypters[encryption_method]

  @classmethod
  def GetDecrypter(cls, encryption_method, **kwargs):
    """Retrieves the decrypter object for a specific encryption method.

    Args:
      encryption_method (str): encryption method identifier.
      kwargs (dict): keyword arguments depending on the decrypter.

    Returns:
      Decrypter: decrypter or None if the encryption method does not exists.

    Raises:
      CredentialError: if the necessary credentials are missing.
    """
    encryption_method = encryption_method.lower()
    decrypter = cls._decrypters.get(encryption_method, None)
    if not decrypter:
      return None

    return decrypter(**kwargs)

  @classmethod
  def RegisterDecrypter(cls, decrypter):
    """Registers a decrypter for a specific encryption method.

    Args:
      decrypter (type): decrypter class.

    Raises:
      KeyError: if the corresponding decrypter is already set.
    """
    encryption_method = decrypter.ENCRYPTION_METHOD.lower()
    if encryption_method in cls._decrypters:
      raise KeyError((
          f'Decrypter for encryption method: {decrypter.ENCRYPTION_METHOD:s} '
          f'already set.'))

    cls._decrypters[encryption_method] = decrypter

  @classmethod
  def RegisterDecrypters(cls, decrypters):
    """Registers decrypters.

    The decrypters are identified based on their lower case encryption method.

    Args:
      decrypters (list[type]): decrypter classes.

    Raises:
      KeyError: if decrypters is already set for the corresponding
          encryption method.
    """
    for decrypter in decrypters:
      cls.RegisterDecrypter(decrypter)
