# -*- coding: utf-8 -*-
"""The root only file system implementation."""

import abc

from dfvfs.lib import errors
from dfvfs.vfs import file_system


class RootOnlyFileSystem(file_system.FileSystem):
  """Class that implements a root only file system object."""

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    return

  def _Open(self, path_spec, mode='rb'):
    """Opens the file system object defined by path specification.

    Args:
      path_spec: a path specification (instance of PathSpec).
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

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      Boolean indicating if the file entry exists.
    """
    return True

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of PathSpec).

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
