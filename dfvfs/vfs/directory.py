# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) directory interface."""


class Directory(object):
  """Directory interface.

  Attributes:
    path_spec (PathSpec): path specification of the directory.
  """

  def __init__(self, file_system, path_spec):
    """Initializes a directory.

    Args:
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
    """
    super(Directory, self).__init__()
    self._entries = None
    self._file_system = file_system
    self.path_spec = path_spec

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Returns:
      generator[PathSpec]: path specification generator.
    """
    return iter(())

  @property
  def entries(self):
    """generator[PathSpec]: path specifications of the directory entries."""
    return self._EntriesGenerator()
