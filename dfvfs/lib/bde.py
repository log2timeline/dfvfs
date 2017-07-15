# -*- coding: utf-8 -*-
"""Helper function for BitLocker Drive Encryption (BDE) support."""

from __future__ import unicode_literals


def BDEVolumeOpen(bde_volume, path_spec, file_object, key_chain):
  """Opens the BDE volume using the path specification.

  Args:
    bde_volume (pybde.volume): BDE volume.
    path_spec (PathSpec): path specification.
    file_object (FileIO): file-like object.
    key_chain (KeyChain): key chain.
  """
  password = key_chain.GetCredential(path_spec, 'password')
  if password:
    bde_volume.set_password(password)

  recovery_password = key_chain.GetCredential(path_spec, 'recovery_password')
  if recovery_password:
    bde_volume.set_recovery_password(recovery_password)

  startup_key = key_chain.GetCredential(path_spec, 'startup_key')
  if startup_key:
    bde_volume.read_startup_key(startup_key)

  bde_volume.open_file_object(file_object)
