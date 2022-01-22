# -*- coding: utf-8 -*-
"""The LUKSDE file system implementation."""

import pyluksde

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import luksde_helper
from dfvfs.path import luksde_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import luksde_file_entry
from dfvfs.vfs import root_only_file_system


class LUKSDEFileSystem(root_only_file_system.RootOnlyFileSystem):
  """File system that uses pyluksde."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_LUKSDE

  def __init__(self, resolver_context, path_spec):
    """Initializes a file system.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(LUKSDEFileSystem, self).__init__(resolver_context, path_spec)
    self._luksde_volume = None
    self._file_object = None

  def _Close(self):
    """Closes the file system.

    Raises:
      IOError: if the close failed.
    """
    self._luksde_volume.close()
    self._luksde_volume = None
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

    luksde_volume = pyluksde.volume()
    file_object = resolver.Resolver.OpenFileObject(
        self._path_spec.parent, resolver_context=self._resolver_context)

    luksde_helper.LUKSDEOpenVolume(
        luksde_volume, self._path_spec, file_object,
        resolver.Resolver.key_chain)

    self._luksde_volume = luksde_volume
    self._file_object = file_object

  def GetLUKSDEVolume(self):
    """Retrieves the LUKSDE volume.

    Returns:
      pyluksde.volume: LUKSDE volume.
    """
    return self._luksde_volume

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      LUKSDEFileEntry: file entry or None.
    """
    return luksde_file_entry.LUKSDEFileEntry(
        self._resolver_context, self, path_spec, is_root=True, is_virtual=True)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      LUKSDEFileEntry: file entry or None.
    """
    path_spec = luksde_path_spec.LUKSDEPathSpec(parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
