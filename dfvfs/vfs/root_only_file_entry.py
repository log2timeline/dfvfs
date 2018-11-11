# -*- coding: utf-8 -*-
"""The root only file system file entry implementation."""

from __future__ import unicode_literals

from dfvfs.vfs import file_entry


class RootOnlyFileEntry(file_entry.FileEntry):
  """Root only file system file entry."""

  # pylint: disable=redundant-returns-doc

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      Directory: a directory or None if not available.
    """
    return None

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Returns:
      generator[FileEntry]: sub file entries.
    """
    return iter(())

  @property
  def name(self):
    """str: name of the file entry, without the full path."""
    return ''
