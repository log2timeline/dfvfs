# -*- coding: utf-8 -*-
"""The Overlay file entry implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import overlay_path_spec
from dfvfs.vfs import file_entry
from dfvfs.vfs import overlay_directory
from dfvfs.resolver import resolver


class OverlayFileEntry(file_entry.FileEntry):
  """File system file entry for Overlay."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_OVERLAY

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False):
    """Initializes an Overlay file entry.

     Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
          entry emulated by the corresponding file system.

    Raises:
      BackEndError: if the parent of the path_spec is empty on a non root
          Overlay file entry.
    """
    if not path_spec.parent and not is_root:
      raise errors.BackEndError('Path spec parent is empty')

    super(OverlayFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)

    location = getattr(path_spec, 'location', None)
    name = ''
    if location:
      location_segments = file_system.SplitPath(location)
      if location_segments:
        name = location_segments[-1]
    self._name = name

    if path_spec.parent:
      parent_filesystem = resolver.Resolver.OpenFileSystem(
          path_spec.parent, resolver_context)
      self._base_file_entry = parent_filesystem.GetFileEntryByPathSpec(
          path_spec.parent)
      self.entry_type = self._base_file_entry.entry_type
    else:
      self._base_file_entry = None

    if is_root:
      self.entry_type = definitions.FILE_ENTRY_TYPE_DIRECTORY

  def _GetAttributes(self):
    """Retrieves the attributes.

    Returns:
      list[Attribute]: attributes.
    """
    if not self._attributes and self._base_file_entry:
      self._attributes = self._base_file_entry._GetAttributes()
    return self._attributes

  def _GetLink(self):
    """Retrieves the link.

    Returns:
      str: path of the linked file.
    """
    if self._base_file_entry:
      return self._base_file_entry._GetLink()
    return None

  def _GetStat(self):
    """Retrieves information about the file entry.

    Returns:
      VFSStat: a stat object.
    """
    if self._base_file_entry:
      return self._base_file_entry._GetStat()
    return None

  def _GetStatAttribute(self):
    """Retrieves a stat attribute.

    Returns:
      StatAttribute: a stat attribute or None if not available.
    """
    if self._base_file_entry:
      return self._base_file_entry._GetStatAttribute()
    return None

  def _GetDataStreams(self):
    """Retrieves the data streams.

    Returns:
      list[DataStream]: data streams.
    """
    if self._base_file_entry:
      return self._base_file_entry._GetDataStreams()
    return []

  def GetFileObject(self, data_stream_name=''):
    """Retrieves a file-like object of a specific data stream.

    Args:
      data_stream_name (Optional[str]): name of the data stream, where an empty
          string represents the default data stream.

    Returns:
      FileIO: a file-like object or None if not available.
    """
    if self._base_file_entry:
      return self._base_file_entry.GetFileObject(data_stream_name)
    return None

  def _GetDirectory(self):
    """Retrieves the directory.

    Returns:
      Directory: a directory.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return None

    return overlay_directory.OverlayDirectory(
        self._file_system, self.path_spec)

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      FileEntry: a sub file entry.
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield OverlayFileEntry(
            self._resolver_context, self._file_system, path_spec)

  @property
  def access_time(self):
    """dfdatetime.DateTimeValues: access time or None if not available."""
    if self._base_file_entry:
      return self._base_file_entry.access_time
    return None

  @property
  def change_time(self):
    """dfdatetime.DateTimeValues: change time or None if not available."""
    if self._base_file_entry:
      return self._base_file_entry.change_time
    return None

  @property
  def creation_time(self):
    """dfdatetime.DateTimeValues: creation time or None if not available."""
    # Creation time can be None if not present and 0 if not set.
    if self._base_file_entry:
      return self._base_file_entry.creation_time
    return None

  @property
  def deletion_time(self):
    """dfdatetime.DateTimeValues: deletion time or None if not available."""
    if self._base_file_entry:
      return self._base_file_entry.deletion_time
    return None

  @property
  def name(self):
    """str: name of the file entry, which does not include the full path."""
    return self._name

  @property
  def modification_time(self):
    """dfdatetime.DateTimeValues: modification time or None if not available."""
    if self._base_file_entry:
      return self._base_file_entry.modification_time
    return None

  @property
  def name(self):
    """str: name of the file entry, which does not include the full path."""
    return self._name

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    if self._base_file_entry:
      return self._base_file_entry.size
    return None

  def GetExtents(self):
    """Retrieves the extents.

    Returns:
      list[Extent]: the extents.
    """
    if self._base_file_entry:
      return self._base_file_entry.GetExtents()
    return []

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      OverlayFileEntry: parent file entry or None if not available.
    """
    parent_location = None

    location = getattr(self.path_spec, 'location', None)
    if location is not None:
      parent_location = self._file_system.DirnamePath(location)
      if parent_location == '':
        parent_location = self._file_system.PATH_SEPARATOR

    parent_path_spec = getattr(self.path_spec, 'parent', None)

    print(parent_path_spec.location)
    path_spec = overlay_path_spec.OverlayPathSpec(
        location=parent_location, parent=parent_path_spec)

    is_root = bool(parent_location == self._file_system.LOCATION_ROOT)

    return OverlayFileEntry(
        self._resolver_context, self._file_system, path_spec, is_root=is_root)
