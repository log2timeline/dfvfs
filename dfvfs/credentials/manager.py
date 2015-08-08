# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) path specification credentials manager object.

The credentials manager uses credential (instances of Credentials) to specify
which credentials a specific path specification type supports. E.g. in case
of  BitLocker Drive Encryption (BDE):
  * password;
  * recovery password;
  * startup key;
  * key data.
"""


class CredentialsManager(object):
  """Class that implements the credentials manager."""

  _credentials = {}

  @classmethod
  def DeregisterCredentials(cls, credentials):
    """Deregisters a path specification credentials.

    Args:
      credentials: the credentials object (instance of credentials.Credentials).

    Raises:
      KeyError: if credential object is not set for the corresponding
                type indicator.
    """
    if credentials.type_indicator not in cls._credentials:
      raise KeyError(
          u'Credential object not set for type indicator: {0:s}.'.format(
              credentials.type_indicator))

    del cls._credentials[credentials.type_indicator]

  @classmethod
  def GetCredentials(cls, path_spec):
    """Retrieves the credentials for a specific path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).

    Returns:
      The credentials (instance of credentials.Credentials) or None if the path
      specification has no credentials support.
    """
    if not path_spec:
      return

    return cls._credentials.get(path_spec.type_indicator, None)

  @classmethod
  def RegisterCredentials(cls, credentials):
    """Registers a path specification credentials.

    Args:
      credentials: the credentials object (instance of credentials.Credentials).

    Raises:
      KeyError: if credentials object is already set for the corresponding
                type indicator.
    """
    if credentials.type_indicator in cls._credentials:
      raise KeyError(
          u'Credentials object already set for type indicator: {0:s}.'.format(
              credentials.type_indicator))

    cls._credentials[credentials.type_indicator] = credentials
