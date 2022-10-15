# -*- coding: utf-8 -*-
"""The XFS file entry implementation."""

from dfdatetime import posix_time as dfdatetime_posix_time

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import xfs_path_spec
from dfvfs.vfs import attribute
from dfvfs.vfs import extent
from dfvfs.vfs import file_entry
from dfvfs.vfs import xfs_attribute
from dfvfs.vfs import xfs_directory


class XFSFileEntry(file_entry.FileEntry):
  """File system file entry that uses pyfsxfs."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_XFS

  # Mappings of XFS file types to dfVFS file entry types.
  _ENTRY_TYPES = {
      0x1000: definitions.FILE_ENTRY_TYPE_PIPE,
      0x2000: definitions.FILE_ENTRY_TYPE_CHARACTER_DEVICE,
      0x4000: definitions.FILE_ENTRY_TYPE_DIRECTORY,
      0x6000: definitions.FILE_ENTRY_TYPE_BLOCK_DEVICE,
      0x8000: definitions.FILE_ENTRY_TYPE_FILE,
      0xa000: definitions.FILE_ENTRY_TYPE_LINK,
      0xc000: definitions.FILE_ENTRY_TYPE_SOCKET}

  def __init__(
      self, resolver_context, file_system, path_spec, fsxfs_file_entry=None,
      is_root=False, is_virtual=False):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      fsxfs_file_entry (Optional[pyfsxfs.file_entry]): XFS file entry.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
          entry emulated by the corresponding file system.

    Raises:
      BackEndError: if the pyfsxfs file entry is missing.
    """
    if not fsxfs_file_entry:
      fsxfs_file_entry = file_system.GetXFSFileEntryByPathSpec(path_spec)
    if not fsxfs_file_entry:
      raise errors.BackEndError('Missing pyfsxfs file entry.')

    if is_root:
      file_entry_name = ''
    else:
      file_entry_name = fsxfs_file_entry.name

    # Use the path specification location to determine the file entry name
    # if the file entry was retrieved by inode.
    if file_entry_name is None:
      location = getattr(path_spec, 'location', None)
      if location:
        location_segments = file_system.SplitPath(location)
        if location_segments:
          file_entry_name = location_segments[-1]

    super(XFSFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._fsxfs_file_entry = fsxfs_file_entry
    self._name = file_entry_name

    self.entry_type = self._ENTRY_TYPES.get(
        fsxfs_file_entry.file_mode & 0xf000, None)

  def _GetAttributes(self):
    """Retrieves the attributes.

    Returns:
      list[Attribute]: attributes.
    """
    if self._attributes is None:
      self._attributes = []

      for fsxfs_extended_attribute in (
          self._fsxfs_file_entry.extended_attributes):
        extended_attribute = xfs_attribute.XFSExtendedAttribute(
            fsxfs_extended_attribute)
        self._attributes.append(extended_attribute)

    return self._attributes

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      XFSDirectory: directory or None if not available.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return None

    return xfs_directory.XFSDirectory(
        self._file_system, self.path_spec, self._fsxfs_file_entry)

  def _GetLink(self):
    """Retrieves the link.

    Returns:
      str: path of the linked file.
    """
    if self._link is None:
      self._link = self._fsxfs_file_entry.symbolic_link_target
      if self._link and self._link[0] != self._file_system.PATH_SEPARATOR:
        # TODO: make link absolute.
        self._link = f'/{self._link:s}'

    return self._link

  def _GetStatAttribute(self):
    """Retrieves a stat attribute.

    Returns:
      StatAttribute: a stat attribute or None if not available.
    """
    stat_attribute = attribute.StatAttribute()
    stat_attribute.device_number = self._fsxfs_file_entry.device_number
    stat_attribute.group_identifier = self._fsxfs_file_entry.group_identifier
    stat_attribute.inode_number = self._fsxfs_file_entry.inode_number
    stat_attribute.mode = self._fsxfs_file_entry.file_mode
    stat_attribute.number_of_links = self._fsxfs_file_entry.number_of_links
    stat_attribute.owner_identifier = self._fsxfs_file_entry.owner_identifier
    stat_attribute.size = self._fsxfs_file_entry.size
    stat_attribute.type = self.entry_type

    return stat_attribute

  def _GetSubFileEntries(self):
    """Retrieves a sub file entries generator.

    Yields:
      XFSFileEntry: a sub file entry.
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield XFSFileEntry(self._resolver_context, self._file_system, path_spec)

  @property
  def access_time(self):
    """dfdatetime.DateTimeValues: access time or None if not available."""
    timestamp = self._fsxfs_file_entry.get_access_time_as_integer()
    return dfdatetime_posix_time.PosixTimeInNanoseconds(timestamp=timestamp)

  @property
  def change_time(self):
    """dfdatetime.DateTimeValues: change time or None if not available."""
    timestamp = self._fsxfs_file_entry.get_inode_change_time_as_integer()
    return dfdatetime_posix_time.PosixTimeInNanoseconds(timestamp=timestamp)

  @property
  def creation_time(self):
    """dfdatetime.DateTimeValues: creation time or None if not available."""
    timestamp = self._fsxfs_file_entry.get_creation_time_as_integer()
    if timestamp is None:
      return None

    return dfdatetime_posix_time.PosixTimeInNanoseconds(timestamp=timestamp)

  @property
  def name(self):
    """str: name of the file entry, which does not include the full path."""
    return self._name

  @property
  def modification_time(self):
    """dfdatetime.DateTimeValues: modification time or None if not available."""
    timestamp = self._fsxfs_file_entry.get_modification_time_as_integer()
    return dfdatetime_posix_time.PosixTimeInNanoseconds(timestamp=timestamp)

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    return self._fsxfs_file_entry.size

  def GetExtents(self):
    """Retrieves the extents.

    Returns:
      list[Extent]: the extents.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_FILE:
      return []

    extents = []
    for extent_index in range(self._fsxfs_file_entry.number_of_extents):
      extent_offset, extent_size, extent_flags = (
          self._fsxfs_file_entry.get_extent(extent_index))

      if extent_flags & 0x1:
        extent_type = definitions.EXTENT_TYPE_SPARSE
      else:
        extent_type = definitions.EXTENT_TYPE_DATA

      data_stream_extent = extent.Extent(
          extent_type=extent_type, offset=extent_offset, size=extent_size)
      extents.append(data_stream_extent)

    return extents

  def GetLinkedFileEntry(self):
    """Retrieves the linked file entry, e.g. for a symbolic link.

    Returns:
      XFSFileEntry: linked file entry or None if not available.
    """
    link = self._GetLink()
    if not link:
      return None

    parent_path_spec = getattr(self.path_spec, 'parent', None)
    path_spec = xfs_path_spec.XFSPathSpec(
        location=link, parent=parent_path_spec)

    is_root = bool(link == self._file_system.LOCATION_ROOT)

    return XFSFileEntry(
        self._resolver_context, self._file_system, path_spec, is_root=is_root)

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      XFSFileEntry: parent file entry or None if not available.
    """
    parent_location = None

    location = getattr(self.path_spec, 'location', None)
    if location is not None:
      parent_location = self._file_system.DirnamePath(location)
      if parent_location == '':
        parent_location = self._file_system.PATH_SEPARATOR

    parent_path_spec = getattr(self.path_spec, 'parent', None)
    path_spec = xfs_path_spec.XFSPathSpec(
        location=parent_location, parent=parent_path_spec)

    is_root = bool(parent_location == self._file_system.LOCATION_ROOT)

    return XFSFileEntry(
        self._resolver_context, self._file_system, path_spec, is_root=is_root)

  def GetXFSFileEntry(self):
    """Retrieves the XFS file entry.

    Returns:
      pyfsxfs.file_entry: XFS file entry.
    """
    return self._fsxfs_file_entry
