# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) path specification key chain object.

The key chain object is used to manage credentials for path specifications.
E.g. BitLocker Drive Encryption (BDE) encrypted volumes can require a
credential (e.g. password) to access the unencrypted data (unlock).
"""

from dfvfs.credentials import manager


class KeyChain(object):
  """Class that implements the key chain."""

  def __init__(self):
    """Initializes the key chain object."""
    super(KeyChain, self).__init__()
    self._credentials_per_path_spec = {}

  def GetCredential(self, path_spec, identifier):
    """Retrieves a specific credential from the key chain.

    Args:
      path_spec: the path specification (instance of PathSpec).
      identifier: string containing the credential identifier.

    Returns:
      The credential or None if the credential for the path specification
      is not set.
    """
    credentials = self._credentials_per_path_spec.get(path_spec.comparable, {})
    return credentials.get(identifier, None)

  def GetCredentials(self, path_spec):
    """Retrieves all credentials for the path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).

    Returns:
      A dictionary containing the credentials which is empty if the credentials
      for the path specification are not set.
    """
    return self._credentials_per_path_spec.get(path_spec.comparable, {})

  def SetCredential(self, path_spec, identifier, data):
    """Sets a specific credential for the path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).
      identifier: string containing the credential identifier.
      data: the credential data.

    Raises:
      KeyError: if the credential is not supported by the path specification
                type.
    """
    supported_credentials = manager.CredentialsManager.GetCredentials(path_spec)

    if identifier not in supported_credentials.CREDENTIALS:
      raise KeyError((
          u'Unsuppored credential: {0:s} for path specification type: '
          u'{1:s}').format(identifier, path_spec.type_indicator))

    credentials = self._credentials_per_path_spec.get(path_spec.comparable, {})
    credentials[identifier] = data
    self._credentials_per_path_spec[path_spec.comparable] = credentials
