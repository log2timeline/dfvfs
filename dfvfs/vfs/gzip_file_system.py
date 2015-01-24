# -*- coding: utf-8 -*-
"""The gzip file system implementation."""

from dfvfs.lib import definitions
from dfvfs.path import gzip_path_spec
from dfvfs.vfs import gzip_file_entry
from dfvfs.vfs import root_only_file_system


class GzipFileSystem(root_only_file_system.RootOnlyFileSystem):
  """Class that implements a file system object using gzip."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_GZIP

  def __init__(self, resolver_context, path_spec):
    """Initializes the file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      path_spec: the path specification (instance of path.PathSpec) of
                 the file-like object.
    """
    super(GzipFileSystem, self).__init__(resolver_context)
    self._path_spec = path_spec

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    path_spec = gzip_path_spec.GzipPathSpec(parent=self._path_spec)
    return gzip_file_entry.GzipFileEntry(
        self._resolver_context, self, path_spec, is_root=True, is_virtual=True)
