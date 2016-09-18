# -*- coding: utf-8 -*-
"""The encrypted stream credentials."""

from dfvfs.credentials import credentials
from dfvfs.credentials import manager
from dfvfs.lib import definitions


class EncryptedStreamCredentials(credentials.Credentials):
  """Class that implements the encrypted stream credentials."""

  CREDENTIALS = frozenset([u'cipher_mode', u'initialization_vector', u'key'])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ENCRYPTED_STREAM


manager.CredentialsManager.RegisterCredentials(EncryptedStreamCredentials())
