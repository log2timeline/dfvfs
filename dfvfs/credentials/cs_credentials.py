# -*- coding: utf-8 -*-
"""The Core Storage (CS) credentials."""

from dfvfs.credentials import credentials
from dfvfs.credentials import manager
from dfvfs.lib import definitions


class CSCredentials(credentials.Credentials):
  """Core Storage (CS) credentials."""

  # TODO: add support for key_data credential, needs pyfvde update.
  CREDENTIALS = frozenset([
      'encrypted_root_plist', 'password', 'recovery_password'])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_CS


manager.CredentialsManager.RegisterCredentials(CSCredentials())
