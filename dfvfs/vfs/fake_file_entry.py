# -*- coding: utf-8 -*-
"""The fake file entry implementation."""

from __future__ import unicode_literals

from dfdatetime import fake_time as dfdatetime_fake_time

from dfvfs.lib import definitions
from dfvfs.file_io import fake_file_io
from dfvfs.path import fake_path_spec
from dfvfs.vfs import file_entry


class FakeDirectory(file_entry.Directory):
  """Fake file system directory."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      FakePathSpec: a path specification.
    """
    location = getattr(self.path_spec, 'location', None)
    if location is not None:
      paths = self._file_system.GetPaths()

      for path in paths.keys():
        # Determine if the start of the path is similar to the location string.
        # If not the file the path refers to is not in the same directory.
        if not path or not path.startswith(location):
          continue

        _, suffix = self._file_system.GetPathSegmentAndSuffix(location, path)

        # Ignore anything that is part of a sub directory or the directory
        # itself.
        if suffix or path == location:
          continue

        path_spec_location = self._file_system.JoinPath([path])
        yield fake_path_spec.FakePathSpec(location=path_spec_location)


class FakeFileEntry(file_entry.FileEntry):
  """Fake file system file entry."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FAKE

  def __init__(
      self, resolver_context, file_system, path_spec, file_entry_type=None,
      is_root=False):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      file_entry_type (Optional[str]): file entry type.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
    """
    super(FakeFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=True)
    self._date_time = dfdatetime_fake_time.FakeTime()
    self._name = None
    self.entry_type = file_entry_type

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      FakeDirectory: a directory.
    """
    if self._directory is None:
      self._directory = FakeDirectory(self._file_system, self.path_spec)

    return self._directory

  def _GetLink(self):
    """Retrieves the link.

    Returns:
      str: full path of the linked file entry.
    """
    if self._link is None:
      self._link = ''

      location = getattr(self.path_spec, 'location', None)
      if location is None:
        return self._link

      self._link = self._file_system.GetDataByPath(location)

    return self._link

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      FakeFileEntry: a sub file entry.
    """
    if self.entry_type == definitions.FILE_ENTRY_TYPE_DIRECTORY:
      directory = self._GetDirectory()
      for path_spec in directory.entries:
        yield self._file_system.GetFileEntryByPathSpec(path_spec)

  @property
  def access_time(self):
    """dfdatetime.DateTimeValues: access time or None if not available."""
    return self._date_time

  @property
  def change_time(self):
    """dfdatetime.DateTimeValues: change time or None if not available."""
    return self._date_time

  @property
  def modification_time(self):
    """dfdatetime.DateTimeValues: modification time or None if not available."""
    return self._date_time

  @property
  def name(self):
    """str: name of the file entry, without the full path."""
    if self._name is None:
      location = getattr(self.path_spec, 'location', None)
      if location is not None:
        self._name = self._file_system.BasenamePath(location)
    return self._name

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    size = None

    location = getattr(self.path_spec, 'location', None)
    if location:
      file_data = self._file_system.GetDataByPath(location)
      if file_data is not None:
        size = len(file_data)

    return size

  def GetFileObject(self, data_stream_name=''):
    """Retrieves the file-like object.

    Args:
      data_stream_name (Optional[str]): name of the data stream, where an empty
          string represents the default data stream.

    Returns:
      FakeFileIO: a file-like object or None if not available.

    Raises:
      IOError: if the file entry is not a file.
      OSError: if the file entry is not a file.
    """
    if not self.IsFile():
      raise IOError('Cannot open non-file.')

    if data_stream_name:
      return None

    location = getattr(self.path_spec, 'location', None)
    if location is None:
      return None

    file_data = self._file_system.GetDataByPath(location)
    file_object = fake_file_io.FakeFile(self._resolver_context, file_data)
    file_object.open(path_spec=self.path_spec)
    return file_object

  def GetParentFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      FakeFileEntry: parent file entry or None if not available.
    """
    location = getattr(self.path_spec, 'location', None)
    if location is None:
      return None

    parent_location = self._file_system.DirnamePath(location)
    if parent_location is None:
      return None

    if parent_location == '':
      parent_location = self._file_system.PATH_SEPARATOR

    path_spec = fake_path_spec.FakePathSpec(location=parent_location)
    return self._file_system.GetFileEntryByPathSpec(path_spec)
