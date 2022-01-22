# -*- coding: utf-8 -*-
"""The BDE file system implementation."""

import pybde

from dfvfs.lib import bde_helper
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import bde_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import bde_file_entry
from dfvfs.vfs import root_only_file_system


class BDEFileSystem(root_only_file_system.RootOnlyFileSystem):
  """File system that uses pybde."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BDE

  def __init__(self, resolver_context, path_spec):
    """Initializes a file system.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(BDEFileSystem, self).__init__(resolver_context, path_spec)
    self._bde_volume = None
    self._file_object = None

  def _Close(self):
    """Closes the file system.

    Raises:
      IOError: if the close failed.
    """
    self._bde_volume.close()
    self._bde_volume = None
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

    bde_volume = pybde.volume()
    file_object = resolver.Resolver.OpenFileObject(
        self._path_spec.parent, resolver_context=self._resolver_context)

    bde_helper.BDEOpenVolume(
        bde_volume, self._path_spec, file_object, resolver.Resolver.key_chain)

    self._bde_volume = bde_volume
    self._file_object = file_object

  def GetBDEVolume(self):
    """Retrieves the BDE volume.

    Returns:
      pybde.volume: BDE volume.
    """
    return self._bde_volume

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      BDEFileEntry: file entry or None.
    """
    return bde_file_entry.BDEFileEntry(
        self._resolver_context, self, path_spec, is_root=True, is_virtual=True)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      BDEFileEntry: file entry or None.
    """
    path_spec = bde_path_spec.BDEPathSpec(parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
