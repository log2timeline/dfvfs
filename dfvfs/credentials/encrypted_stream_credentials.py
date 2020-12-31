# -*- coding: utf-8 -*-
"""The encrypted stream credentials."""

from dfvfs.credentials import credentials
from dfvfs.credentials import manager
from dfvfs.lib import definitions


class EncryptedStreamCredentials(credentials.Credentials):
  """Encrypted stream credentials."""

  CREDENTIALS = frozenset(['cipher_mode', 'initialization_vector', 'key'])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ENCRYPTED_STREAM


manager.CredentialsManager.RegisterCredentials(EncryptedStreamCredentials())
