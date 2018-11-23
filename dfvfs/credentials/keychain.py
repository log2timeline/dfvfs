# -*- coding: utf-8 -*-
"""The path specification key chain.

The key chain is used to manage credentials for path specifications.
E.g. BitLocker Drive Encryption (BDE) encrypted volumes can require a
credential (e.g. password) to access the unencrypted data (unlock).
"""

from __future__ import unicode_literals

from dfvfs.credentials import manager


class KeyChain(object):
  """Key chain."""

  def __init__(self):
    """Initializes a key chain."""
    super(KeyChain, self).__init__()
    self._credentials_per_path_spec = {}

  def Empty(self):
    """Empties the key chain."""
    self._credentials_per_path_spec = {}

  def ExtractCredentialsFromPathSpec(self, path_spec):
    """Extracts credentials from a path specification.

    Args:
      path_spec (PathSpec): path specification to extract credentials from.
    """
    credentials = manager.CredentialsManager.GetCredentials(path_spec)
    for identifier in credentials.CREDENTIALS:
      value = getattr(path_spec, identifier, None)
      if value is None:
        continue

      self.SetCredential(path_spec, identifier, value)

  def GetCredential(self, path_spec, identifier):
    """Retrieves a specific credential from the key chain.

    Args:
      path_spec (PathSpec): path specification.
      identifier (str): credential identifier.

    Returns:
      object: credential or None if the credential for the path specification
          is not set.
    """
    credentials = self._credentials_per_path_spec.get(path_spec.comparable, {})
    return credentials.get(identifier, None)

  def GetCredentials(self, path_spec):
    """Retrieves all credentials for the path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      dict[str,object]: credentials for the path specification.
    """
    return self._credentials_per_path_spec.get(path_spec.comparable, {})

  def SetCredential(self, path_spec, identifier, data):
    """Sets a specific credential for the path specification.

    Args:
      path_spec (PathSpec): path specification.
      identifier (str): credential identifier.
      data (object): credential data.

    Raises:
      KeyError: if the credential is not supported by the path specification
          type.
    """
    supported_credentials = manager.CredentialsManager.GetCredentials(path_spec)

    if identifier not in supported_credentials.CREDENTIALS:
      raise KeyError((
          'Unsuppored credential: {0:s} for path specification type: '
          '{1:s}').format(identifier, path_spec.type_indicator))

    credentials = self._credentials_per_path_spec.get(path_spec.comparable, {})
    credentials[identifier] = data
    self._credentials_per_path_spec[path_spec.comparable] = credentials
