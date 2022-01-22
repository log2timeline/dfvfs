# -*- coding: utf-8 -*-
"""The FVDE file system implementation."""

import pyfvde

from dfvfs.lib import decorators
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import fvde_helper
from dfvfs.path import fvde_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import fvde_file_entry
from dfvfs.vfs import root_only_file_system


class FVDEFileSystem(root_only_file_system.RootOnlyFileSystem):
  """Class that implements a file system using FVDE."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FVDE

  def __init__(self, resolver_context, path_spec):
    """Initializes a file system.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(FVDEFileSystem, self).__init__(resolver_context, path_spec)
    self._fvde_volume = None
    self._file_object = None

  def _Close(self):
    """Closes the file system.

    Raises:
      IOError: if the close failed.
    """
    self._fvde_volume.close()
    self._fvde_volume = None
    self._file_object = None

  def _Open(self, mode='rb'):
    """Opens the file system defined by path specification.

    Args:
      mode (Optional[str]): file access mode. The default is 'rb'
          read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not self._path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    resolver.Resolver.key_chain.ExtractCredentialsFromPathSpec(self._path_spec)

    fvde_volume = pyfvde.volume()
    file_object = resolver.Resolver.OpenFileObject(
        self._path_spec.parent, resolver_context=self._resolver_context)

    fvde_helper.FVDEOpenVolume(
        fvde_volume, self._path_spec, file_object, resolver.Resolver.key_chain)

    self._fvde_volume = fvde_volume
    self._file_object = file_object

  @decorators.deprecated
  def GetFVDEVolume(self):
    """Retrieves the FVDE volume.

    Returns:
      pyfvde.volume: FVDE volume.
    """
    return self._fvde_volume

  @decorators.deprecated
  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      FVDEFileEntry: file entry or None.
    """
    return fvde_file_entry.FVDEFileEntry(
        self._resolver_context, self, path_spec, is_root=True, is_virtual=True)

  @decorators.deprecated
  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      FVDEFileEntry: file entry or None.
    """
    path_spec = fvde_path_spec.FVDEPathSpec(parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
