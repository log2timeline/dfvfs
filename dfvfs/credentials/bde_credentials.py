# -*- coding: utf-8 -*-
"""The BitLocker Drive Encryption (BDE) credentials."""

from __future__ import unicode_literals

from dfvfs.credentials import credentials
from dfvfs.credentials import manager
from dfvfs.lib import definitions


# TODO: add means to set the credentials in the bde_volume using the helper?


class BDECredentials(credentials.Credentials):
  """BitLocker Drive Encryption (BDE) credentials."""

  # TODO: add support for key_data credential, needs pybde update.
  CREDENTIALS = frozenset([
      'password', 'recovery_password', 'startup_key'])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BDE


manager.CredentialsManager.RegisterCredentials(BDECredentials())
