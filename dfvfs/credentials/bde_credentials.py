# -*- coding: utf-8 -*-
"""The BitLocker Drive Encryption (BDE) credentials object."""

from dfvfs.credentials import credentials
from dfvfs.credentials import manager
from dfvfs.lib import definitions


# TODO: add means to set the credentials in the bde_volume using the helper?


class BDECredentials(credentials.Credentials):
  """Class that implements the BDE credentials object."""

  # TODO: add support for key_data credential, needs pybde update.
  CREDENTIALS = frozenset([
      u'password', u'recovery_password', u'startup_key'])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BDE


manager.CredentialsManager.RegisterCredentials(BDECredentials())
