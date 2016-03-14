# -*- coding: utf-8 -*-
"""Helper function for BitLocker Drive Encryption (BDE) support."""


def BDEVolumeOpen(bde_volume, path_spec, file_object, key_chain):
  """Opens the BDE volume using the path specification.

  Args:
    bde_volume: the BDE volume (instance of pybde.volume).
    path_spec: the path specification (instance of PathSpec).
    file_object: the file-like object (instance of FileIO).
    key_chain: the key chain (instance of credentials.KeyChain).
  """
  password = key_chain.GetCredential(path_spec, u'password')
  if password:
    bde_volume.set_password(password)

  recovery_password = key_chain.GetCredential(path_spec, u'recovery_password')
  if recovery_password:
    bde_volume.set_recovery_password(recovery_password)

  startup_key = key_chain.GetCredential(path_spec, u'startup_key')
  if startup_key:
    bde_volume.read_startup_key(startup_key)

  bde_volume.open_file_object(file_object)
