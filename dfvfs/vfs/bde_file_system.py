# -*- coding: utf-8 -*-
"""The BDE file system implementation."""

import pybde

from dfvfs.lib import bde
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import bde_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import bde_file_entry
from dfvfs.vfs import root_only_file_system


class BdeFileSystem(root_only_file_system.RootOnlyFileSystem):
  """Class that implements a file system object using BDE."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BDE

  def __init__(self, resolver_context):
    """Initializes a file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
    """
    super(BdeFileSystem, self).__init__(resolver_context)
    self._bde_volume = None
    self._file_object = None

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    self._bde_volume.close()
    self._bde_volume = None

    self._file_object.close()
    self._file_object = None

  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file system object defined by path specification.

    Args:
      path_spec: optional path specification (instance of path.PathSpec).
                 The default is None.
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          u'Unsupported path specification without parent.')

    bde_volume = pybde.volume()
    file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=self._resolver_context)

    bde.BdeVolumeOpen(
        bde_volume, path_spec, file_object, resolver.Resolver.key_chain)

    self._bde_volume = bde_volume
    self._file_object = file_object

  def GetBdeVolume(self):
    """Retrieves the BDE volume object.

    Returns:
      The BDE volume object (instance of pybde.volume).
    """
    return self._bde_volume

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    return bde_file_entry.BdeFileEntry(
        self._resolver_context, self, path_spec, is_root=True, is_virtual=True)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    path_spec = bde_path_spec.BdePathSpec(parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
