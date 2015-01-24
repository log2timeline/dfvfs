# -*- coding: utf-8 -*-
"""The root only file system implementation."""

import abc

from dfvfs.vfs import file_system


class RootOnlyFileSystem(file_system.FileSystem):
  """Class that implements a root only file system object."""

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      Boolean indicating if the file entry exists.
    """
    return True

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    return self.GetRootFileEntry()

  @abc.abstractmethod
  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
