# -*- coding: utf-8 -*-
"""The LUKS Drive Encryption credentials."""

from dfvfs.credentials import credentials
from dfvfs.credentials import manager
from dfvfs.lib import definitions


class LUKSDECredentials(credentials.Credentials):
  """LUKS Drive Encryption credentials."""

  # TODO: add support for key_data credential.
  CREDENTIALS = frozenset([
      'password'])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_LUKSDE


manager.CredentialsManager.RegisterCredentials(LUKSDECredentials())
