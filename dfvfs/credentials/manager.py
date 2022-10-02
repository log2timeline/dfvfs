# -*- coding: utf-8 -*-
"""The path specification credentials manager.

The credentials manager uses credential (instances of Credentials) to specify
which credentials a specific path specification type supports. E.g. in case
of BitLocker Drive Encryption (BDE):
* password;
* recovery password;
* startup key;
* key data.
"""


class CredentialsManager(object):
  """Credentials manager."""

  _credentials = {}

  @classmethod
  def DeregisterCredentials(cls, credentials):
    """Deregisters a path specification credentials.

    Args:
      credentials (Credentials): credentials.

    Raises:
      KeyError: if credential object is not set for the corresponding
          type indicator.
    """
    if credentials.type_indicator not in cls._credentials:
      raise KeyError((
          f'Credential object not set for type indicator: '
          f'{credentials.type_indicator:s}.'))

    del cls._credentials[credentials.type_indicator]

  @classmethod
  def GetCredentials(cls, path_spec):
    """Retrieves the credentials for a specific path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      Credentials: credentials or None if the path specification has no
          credentials support.
    """
    if not path_spec:
      return None

    return cls._credentials.get(path_spec.type_indicator, None)

  @classmethod
  def RegisterCredentials(cls, credentials):
    """Registers a path specification credentials.

    Args:
      credentials (Credentials): credentials.

    Raises:
      KeyError: if credentials object is already set for the corresponding
          type indicator.
    """
    if credentials.type_indicator in cls._credentials:
      raise KeyError((
          f'Credentials object already set for type indicator: '
          f'{credentials.type_indicator:s}.'))

    cls._credentials[credentials.type_indicator] = credentials
