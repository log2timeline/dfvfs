# -*- coding: utf-8 -*-
"""A builder for fake file systems."""

from dfvfs.lib import definitions
from dfvfs.path import fake_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import fake_file_system


class FakeFileSystemBuilder(object):
  """Builder object for fake file systems.

  Attributes:
    file_system (FakeFileSystem): fake file system.
  """

  def __init__(self):
    """Initializes a fake file system builder."""
    super(FakeFileSystemBuilder, self).__init__()
    resolver_context = context.Context()
    path_spec = fake_path_spec.FakePathSpec(location='/')
    self.file_system = fake_file_system.FakeFileSystem(
        resolver_context, path_spec)

  def _AddParentDirectories(self, path):
    """Adds the parent directories of a path to the fake file system.

    Args:
      path (str): path of the file within the fake file system.

    Raises:
      ValueError: if a parent directory is already set and is not a directory.
    """
    path_segments = self.file_system.SplitPath(path)
    for segment_index in range(len(path_segments)):
      parent_path = self.file_system.JoinPath(path_segments[:segment_index])
      file_entry = self.file_system.GetFileEntryByPath(parent_path)
      if file_entry and not file_entry.IsDirectory():
        raise ValueError(
            f'Non-directory parent file entry: {parent_path:s} already exists.')

    for segment_index in range(len(path_segments)):
      parent_path = self.file_system.JoinPath(path_segments[:segment_index])
      if not self.file_system.FileEntryExistsByPath(parent_path):
        self.file_system.AddFileEntry(
            parent_path, file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

  def AddDirectory(self, path):
    """Adds a directory to the fake file system.

    Note that this function will create parent directories if needed.

    Args:
      path (str): path of the directory within the fake file system.

    Raises:
      ValueError: if the path is already set.
    """
    if self.file_system.FileEntryExistsByPath(path):
      raise ValueError(f'Path: {path:s} already set.')

    self._AddParentDirectories(path)
    self.file_system.AddFileEntry(
        path, file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

  def AddFile(self, path, file_data):
    """Adds a "regular" file to the fake file system.

    Note that this function will create parent directories if needed.

    Args:
      path (str): path of the file within the fake file system.
      file_data (bytes): data of the file.

    Raises:
      ValueError: if the path is already set.
    """
    if self.file_system.FileEntryExistsByPath(path):
      raise ValueError(f'Path: {path:s} already set.')

    self._AddParentDirectories(path)
    self.file_system.AddFileEntry(path, file_data=file_data)

  def AddFileReadData(self, path, file_data_path):
    """Adds a "regular" file to the fake file system.

    Args:
      path (str): path of the file within the fake file system.
      file_data_path (str): path of the file to read the file data from.

    Raises:
      ValueError: if the path is already set.
    """
    if self.file_system.FileEntryExistsByPath(path):
      raise ValueError(f'Path: {path:s} already set.')

    with open(file_data_path, 'rb') as file_object:
      file_data = file_object.read()

    self._AddParentDirectories(path)
    self.file_system.AddFileEntry(path, file_data=file_data)

  def AddSymbolicLink(self, path, linked_path):
    """Adds a symbolic link to the fake file system.

    Args:
      path (str): path of the symbolic link within the fake file system.
      linked_path (str): path that is linked.

    Raises:
      ValueError: if the path is already set.
    """
    if self.file_system.FileEntryExistsByPath(path):
      raise ValueError(f'Path: {path:s} already set.')

    self._AddParentDirectories(path)
    self.file_system.AddFileEntry(
        path, file_entry_type=definitions.FILE_ENTRY_TYPE_LINK,
        link_data=linked_path)
