# -*- coding: utf-8 -*-
"""Helper function for BitLocker Drive Encryption (BDE) support."""


def BDEVolumeOpen(bde_volume, credentials, file_object):
  """Opens the BDE volume using the path specification.

  Args:
    bde_volume: the BDE volume (instance of pybde.volume).
    credentials: a dictionary of credentials.
    file_object: the file-like object (instance of FileIO).
  """
  password = credentials.get(u'password', None)
  if password is not None:
    bde_volume.set_password(password)

  recovery_password = credentials.get(u'recovery_password', None)
  if recovery_password is not None:
    bde_volume.set_recovery_password(recovery_password)

  startup_key = credentials.get(u'startup_key', None)
  if startup_key is not None:
    bde_volume.read_startup_key(startup_key)

  bde_volume.open_file_object(file_object)
