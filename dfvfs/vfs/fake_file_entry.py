# -*- coding: utf-8 -*-
"""The fake file entry implementation."""

from dfvfs.lib import definitions
from dfvfs.file_io import fake_file_io
from dfvfs.path import fake_path_spec
from dfvfs.vfs import file_entry


class FakeDirectory(file_entry.Directory):
  """Class that implements a fake directory object."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      A path specification (instance of path.FakePathSpec).
    """
    location = getattr(self.path_spec, u'location', None)
    if location is None:
      return

    paths = self._file_system.GetPaths()

    for path in iter(paths.keys()):
      # Determine if the start of the path is similar to the location string.
      # If not the file the path refers to is not in the same directory.
      if not path or not path.startswith(location):
        continue

      _, suffix = self._file_system.GetPathSegmentAndSuffix(location, path)

      # Ignore anything that is part of a sub directory or the directory itself.
      if suffix or path == location:
        continue

      path_spec_location = self._file_system.JoinPath([path])
      yield fake_path_spec.FakePathSpec(location=path_spec_location)


class FakeFileEntry(file_entry.FileEntry):
  """Class that implements a fake file entry object."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FAKE

  def __init__(self, resolver_context, file_system, path_spec, is_root=False):
    """Initializes the file entry object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      file_system: the file system object (instance of FileSystem).
      path_spec: the path specification object (instance of PathSpec).
      is_root: optional boolean value to indicate if the file entry is
               the root file entry of the corresponding file system.
    """
    super(FakeFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=True)
    self._name = None

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      A directory object (instance of Directory) or None.
    """
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if (self._stat_object and
        self._stat_object.type == self._stat_object.TYPE_DIRECTORY):
      return FakeDirectory(self._file_system, self.path_spec)
    return

  def _GetStat(self):
    """Retrieves the stat object (instance of vfs.VFSStat)."""
    location = getattr(self.path_spec, u'location', None)
    if location is None:
      return

    return self._file_system.GetStatObjectByPath(location)

  @property
  def link(self):
    """The full path of the linked file entry."""
    if not self.IsLink():
      return u''

    location = getattr(self.path_spec, u'location', None)
    if location is None:
      return u''

    return self._file_system.GetDataByPath(location)

  @property
  def name(self):
    """The name of the file entry, which does not include the full path."""
    if self._name is None:
      location = getattr(self.path_spec, u'location', None)
      if location is not None:
        self._name = self._file_system.BasenamePath(location)
    return self._name

  @property
  def sub_file_entries(self):
    """The sub file entries (generator of instance of vfs.FakeFileEntry)."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield FakeFileEntry(
            self._resolver_context, self._file_system, path_spec)

  def GetFileObject(self, data_stream_name=u''):
    """Retrieves the file-like object.

    Args:
      data_stream_name: optional data stream name. The default is
                        an empty string which represents the default
                        data stream.

    Returns:
      A file-like object (instance of file_io.FileIO) or None.

    Raises:
      IOError: if the file entry is not a file.
    """
    if not self.IsFile():
      raise IOError(u'Cannot open non-file.')

    if data_stream_name:
      return

    location = getattr(self.path_spec, u'location', None)
    if location is None:
      return

    file_data = self._file_system.GetDataByPath(location)
    file_object = fake_file_io.FakeFile(self._resolver_context, file_data)
    file_object.open(path_spec=self.path_spec)
    return file_object

  def GetParentFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      The parent file entry (instance of FileEntry) or None.
    """
    location = getattr(self.path_spec, u'location', None)
    if location is None:
      return

    parent_location = self._file_system.DirnamePath(location)
    if parent_location is None:
      return

    if parent_location == u'':
      parent_location = self._file_system.PATH_SEPARATOR

    path_spec = fake_path_spec.FakePathSpec(location=parent_location)
    return FakeFileEntry(self._resolver_context, self._file_system, path_spec)
