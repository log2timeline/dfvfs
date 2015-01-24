# -*- coding: utf-8 -*-
"""The BDE file system implementation."""

from dfvfs.lib import definitions
from dfvfs.path import bde_path_spec
from dfvfs.vfs import bde_file_entry
from dfvfs.vfs import root_only_file_system


class BdeFileSystem(root_only_file_system.RootOnlyFileSystem):
  """Class that implements a file system object using BDE."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BDE

  def __init__(self, resolver_context, bde_volume, path_spec):
    """Initializes the file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      bde_volume: the BDE volume object (instance of pybde.volume).
      path_spec: the path specification (instance of path.PathSpec) of
                 the file-like object.
    """
    super(BdeFileSystem, self).__init__(resolver_context)
    self._bde_volume = bde_volume
    self._path_spec = path_spec

  def GetBdeVolume(self):
    """Retrieves the BDE volume object.

    Returns:
      The BDE volume object (instance of pybde.volume).
    """
    return self._bde_volume

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    path_spec = bde_path_spec.BdePathSpec(parent=self._path_spec)
    return bde_file_entry.BdeFileEntry(
        self._resolver_context, self, path_spec, is_root=True, is_virtual=True)
