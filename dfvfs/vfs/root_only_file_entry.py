# -*- coding: utf-8 -*-
"""The root only file entry implementation."""

import abc

from dfvfs.vfs import file_entry


class RootOnlyFileEntry(file_entry.FileEntry):
  """Class that implements a root only file entry object."""

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      A directory object (instance of Directory) or None.
    """
    return

  @abc.abstractmethod
  def _GetStat(self):
    """Retrieves the stat object (instance of vfs.VFSStat)."""

  @property
  def name(self):
    """The name of the file entry, which does not include the full path."""
    return u''

  @property
  def sub_file_entries(self):
    """The sub file entries (generator of instance of vfs.FileEntry)."""
    # We are creating an empty generator here. Yield or return None
    # individually don't provide that behavior, neither does raising
    # GeneratorExit or StopIteration.
    # pylint: disable=unreachable
    return
    yield
