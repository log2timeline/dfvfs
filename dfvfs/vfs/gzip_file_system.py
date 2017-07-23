# -*- coding: utf-8 -*-
"""The gzip file system implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.path import gzip_path_spec
from dfvfs.vfs import gzip_file_entry
from dfvfs.vfs import root_only_file_system


class GzipFileSystem(root_only_file_system.RootOnlyFileSystem):
  """File system that uses gzip."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_GZIP

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      GzipFileEntry: a file entry or None if not available.
    """
    return gzip_file_entry.GzipFileEntry(
        self._resolver_context, self, path_spec, is_root=True, is_virtual=True)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      GzipFileEntry: a file entry or None if not available.
    """
    path_spec = gzip_path_spec.GzipPathSpec(parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
