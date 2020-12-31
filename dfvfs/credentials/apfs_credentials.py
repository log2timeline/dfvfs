# -*- coding: utf-8 -*-
"""The Apple File System (APFS) credentials."""

from dfvfs.credentials import credentials
from dfvfs.credentials import manager
from dfvfs.lib import definitions


class APFSCredentials(credentials.Credentials):
  """Apple File System (APFS) credentials."""

  # TODO: add support for key_data credential, needs pyfsapfs update.
  CREDENTIALS = frozenset(['password', 'recovery_password'])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_APFS_CONTAINER


manager.CredentialsManager.RegisterCredentials(APFSCredentials())
