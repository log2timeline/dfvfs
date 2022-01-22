# -*- coding: utf-8 -*-
"""The LUKS Drive Encryption file-like object."""

import pyluksde

from dfvfs.file_io import file_object_io
from dfvfs.lib import luksde_helper
from dfvfs.lib import errors
from dfvfs.resolver import resolver


class LUKSDEFile(file_object_io.FileObjectIO):
  """File input/output (IO) object using pyluksde."""

  def _OpenFileObject(self, path_spec):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      pyvde.volume: LUKSDE volume file-like object.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    resolver.Resolver.key_chain.ExtractCredentialsFromPathSpec(path_spec)

    file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=self._resolver_context)
    luksde_volume = pyluksde.volume()

    luksde_helper.LUKSDEOpenVolume(
        luksde_volume, path_spec, file_object, resolver.Resolver.key_chain)
    return luksde_volume

  @property
  def is_locked(self):
    """bool: True if the volume is locked."""
    return self._file_object.is_locked()
