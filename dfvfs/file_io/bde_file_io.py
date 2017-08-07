# -*- coding: utf-8 -*-
"""The BitLocker Drive Encryption (BDE) file-like object."""

from __future__ import unicode_literals

import pybde

from dfvfs.file_io import file_object_io
from dfvfs.lib import bde
from dfvfs.lib import errors
from dfvfs.resolver import resolver


class BDEFile(file_object_io.FileObjectIO):
  """File-like object using pybde."""

  def _OpenFileObject(self, path_spec):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      pyvde.volume: BDE volume file-like object.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    resolver.Resolver.key_chain.ExtractCredentialsFromPathSpec(path_spec)

    file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=self._resolver_context)
    bde_volume = pybde.volume()

    bde.BDEVolumeOpen(
        bde_volume, path_spec, file_object, resolver.Resolver.key_chain)
    return bde_volume

  @property
  def is_locked(self):
    """bool: True if the volume is locked."""
    return self._file_object.is_locked()
