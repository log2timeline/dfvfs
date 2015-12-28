# -*- coding: utf-8 -*-
"""The encrypted stream credentials object."""

from dfvfs.credentials import credentials
from dfvfs.credentials import manager
from dfvfs.lib import definitions


class EncryptedStreamCredendials(credentials.Credentials):
  """Class that implements the encrypted stream credentials object."""

  CREDENTIALS = frozenset([u'key'])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ENCRYPTED_STREAM


# Register the resolver helpers with the resolver.
manager.CredentialsManager.RegisterCredentials(EncryptedStreamCredendials())
