# -*- coding: utf-8 -*-
"""The fake file system implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import fake_path_spec
from dfvfs.vfs import file_system
from dfvfs.vfs import fake_file_entry


class FakeFileSystem(file_system.FileSystem):
  """Fake file system."""

  LOCATION_ROOT = '/'

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FAKE

  def __init__(self, resolver_context):
    """Initializes a file system.

    Args:
      resolver_context (Context): a resolver context.
    """
    super(FakeFileSystem, self).__init__(resolver_context)
    self._paths = {}

    self.AddFileEntry(
        self.LOCATION_ROOT,
        file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

  def _Close(self):
    """Closes the file system.

    Raises:
      IOError: if the close failed.
    """
    return

  def _Open(self, path_spec, mode='rb'):
    """Opens the file system defined by path specification.

    Args:
      path_spec (PathSpec): path specification.
      mode (Optional[str]): file access mode. The default is 'rb' which
          represents read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification with parent.')

  def AddFileEntry(
      self, path, file_entry_type=definitions.FILE_ENTRY_TYPE_FILE,
      file_data=None, link_data=None):
    """Adds a fake file entry.

    Args:
      path (str): path of the file entry.
      file_entry_type (Optional[str]): type of the file entry object.
      file_data (Optional[bytes]): data of the fake file-like object.
      link_data (Optional[bytes]): link data of the fake file entry object.

    Raises:
      KeyError: if the path already exists.
      ValueError: if the file data is set but the file entry type is not a file
          or if the link data is set but the file entry type is not a link.
    """
    if path in self._paths:
      raise KeyError('File entry already set for path: {0:s}.'.format(path))

    if file_data and file_entry_type != definitions.FILE_ENTRY_TYPE_FILE:
      raise ValueError('File data set for non-file file entry type.')

    if link_data and file_entry_type != definitions.FILE_ENTRY_TYPE_LINK:
      raise ValueError('Link data set for non-link file entry type.')

    if file_data is not None:
      path_data = file_data
    elif link_data is not None:
      path_data = link_data
    else:
      path_data = None

    self._paths[path] = (file_entry_type, path_data)

  def FileEntryExistsByPath(self, path):
    """Determines if a file entry for a path exists.

    Args:
      path (str): path of the file entry.

    Returns:
      bool: True if the file entry exists.
    """
    return path and path in self._paths

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      bool: True if the file entry exists.
    """
    location = getattr(path_spec, 'location', None)
    return self.FileEntryExistsByPath(location)

  def GetDataByPath(self, path):
    """Retrieves the data associated to a path.

    Args:
      path (str): path of the file entry.

    Returns:
      bytes: data or None if not available.
    """
    _, path_data = self._paths.get(path, (None, None))
    return path_data

  def GetFileEntryByPath(self, path):
    """Retrieves a file entry for a path.

    Args:
      path (str): path of the file entry.

    Returns:
      FakeFileEntry: a file entry or None if not available.
    """
    if path is None:
      return None

    file_entry_type, _ = self._paths.get(path, (None, None))
    if not file_entry_type:
      return None

    path_spec = fake_path_spec.FakePathSpec(location=path)
    is_root = bool(path == self.LOCATION_ROOT)
    return fake_file_entry.FakeFileEntry(
        self._resolver_context, self, path_spec,
        file_entry_type=file_entry_type, is_root=is_root)

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      FakeFileEntry: a file entry or None if not available.
    """
    location = getattr(path_spec, 'location', None)
    return self.GetFileEntryByPath(location)

  def GetPaths(self):
    """Retrieves the paths dictionary.

    Returns:
      dict[str, FileIO]: file-like object per path.
    """
    return self._paths

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      FakeFileEntry: a file entry or None if not available.
    """
    path_spec = fake_path_spec.FakePathSpec(location=self.LOCATION_ROOT)
    return self.GetFileEntryByPathSpec(path_spec)
