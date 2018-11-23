# -*- coding: utf-8 -*-
"""The FileVault Drive Encryption (FVDE) credentials."""

from __future__ import unicode_literals

from dfvfs.credentials import credentials
from dfvfs.credentials import manager
from dfvfs.lib import definitions


# TODO: add means to set the credentials in the fvde_volume using the helper?


class FVDECredentials(credentials.Credentials):
  """FileVault Drive Encryption (FVDE) credentials."""

  # TODO: add support for key_data credential, needs pyfvde update.
  CREDENTIALS = frozenset([
      'encrypted_root_plist', 'password', 'recovery_password'])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FVDE


manager.CredentialsManager.RegisterCredentials(FVDECredentials())
