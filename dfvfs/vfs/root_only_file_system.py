# -*- coding: utf-8 -*-
"""The root only file system implementation."""

import abc

from dfvfs.lib import errors
from dfvfs.vfs import file_system


class RootOnlyFileSystem(file_system.FileSystem):
  """Root only file system."""

  # pylint: disable=redundant-returns-doc

  def _Close(self):
    """Closes the file system.

    Raises:
      IOError: if the close failed.
    """
    return

  def _Open(self, mode='rb'):
    """Opens the file system defined by path specification.

    Args:
      mode (Optional[str]): file access mode. The default is 'rb' which
          represents read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not self._path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      bool: True if the file entry exists.
    """
    return True

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      FileEntry: a file entry or None if not available.
    """
    return self.GetRootFileEntry()

  @abc.abstractmethod
  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      FileEntry: a file entry or None if not available.
    """
