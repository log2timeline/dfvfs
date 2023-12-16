# -*- coding: utf-8 -*-
"""The EXT file entry implementation."""

from dfdatetime import posix_time as dfdatetime_posix_time

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import ext_path_spec
from dfvfs.vfs import attribute
from dfvfs.vfs import ext_attribute
from dfvfs.vfs import ext_directory
from dfvfs.vfs import extent
from dfvfs.vfs import file_entry


class EXTFileEntry(file_entry.FileEntry):
  """File system file entry that uses pyfsext."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_EXT

  # Mappings of EXT file types to dfVFS file entry types.
  _ENTRY_TYPES = {
      0x1000: definitions.FILE_ENTRY_TYPE_PIPE,
      0x2000: definitions.FILE_ENTRY_TYPE_CHARACTER_DEVICE,
      0x4000: definitions.FILE_ENTRY_TYPE_DIRECTORY,
      0x6000: definitions.FILE_ENTRY_TYPE_BLOCK_DEVICE,
      0x8000: definitions.FILE_ENTRY_TYPE_FILE,
      0xa000: definitions.FILE_ENTRY_TYPE_LINK,
      0xc000: definitions.FILE_ENTRY_TYPE_SOCKET}

  _NANOSECONDS_PER_SECOND = 1000000000

  def __init__(
      self, resolver_context, file_system, path_spec, fsext_file_entry=None,
      is_root=False, is_virtual=False):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      fsext_file_entry (Optional[pyfsext.file_entry]): EXT file entry.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
          entry emulated by the corresponding file system.

    Raises:
      BackEndError: if the pyfsext file entry is missing.
    """
    if not fsext_file_entry:
      fsext_file_entry = file_system.GetEXTFileEntryByPathSpec(path_spec)
    if not fsext_file_entry:
      raise errors.BackEndError('Missing pyfsext file entry.')

    if is_root:
      file_entry_name = ''
    else:
      file_entry_name = fsext_file_entry.name

    # Use the path specification location to determine the file entry name
    # if the file entry was retrieved by inode.
    if file_entry_name is None:
      location = getattr(path_spec, 'location', None)
      if location:
        location_segments = file_system.SplitPath(location)
        if location_segments:
          file_entry_name = location_segments[-1]

    super(EXTFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._creation_time = fsext_file_entry.get_creation_time_as_integer()
    self._fsext_file_entry = fsext_file_entry
    self._name = file_entry_name

    self.entry_type = self._ENTRY_TYPES.get(
        fsext_file_entry.file_mode & 0xf000, None)

  def _GetAttributes(self):
    """Retrieves the attributes.

    Returns:
      list[Attribute]: attributes.
    """
    if self._attributes is None:
      self._attributes = []

      for fsext_extended_attribute in (
          self._fsext_file_entry.extended_attributes):
        extended_attribute = ext_attribute.EXTExtendedAttribute(
            fsext_extended_attribute)
        self._attributes.append(extended_attribute)

    return self._attributes

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      EXTDirectory: directory or None if not available.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return None

    return ext_directory.EXTDirectory(
        self._file_system, self.path_spec, self._fsext_file_entry)

  def _GetLink(self):
    """Retrieves the link.

    Returns:
      str: path of the linked file.
    """
    if self._link is None:
      self._link = self._fsext_file_entry.symbolic_link_target
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
    stat_attribute.device_number = self._fsext_file_entry.device_number
    stat_attribute.group_identifier = self._fsext_file_entry.group_identifier
    stat_attribute.inode_number = self._fsext_file_entry.inode_number
    stat_attribute.mode = self._fsext_file_entry.file_mode
    stat_attribute.number_of_links = self._fsext_file_entry.number_of_links
    stat_attribute.owner_identifier = self._fsext_file_entry.owner_identifier
    stat_attribute.size = self._fsext_file_entry.size
    stat_attribute.type = self.entry_type

    return stat_attribute

  def _GetSubFileEntries(self):
    """Retrieves a sub file entries generator.

    Yields:
      EXTFileEntry: a sub file entry.
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield EXTFileEntry(self._resolver_context, self._file_system, path_spec)

  @property
  def access_time(self):
    """dfdatetime.DateTimeValues: access time or None if not available."""
    timestamp = self._fsext_file_entry.get_access_time_as_integer()

    # If creation time is not present (None) the timestamp precision is in
    # seconds.
    if self._creation_time is None:
      timestamp, _ = divmod(timestamp, self._NANOSECONDS_PER_SECOND)
      return dfdatetime_posix_time.PosixTime(timestamp=timestamp)

    return dfdatetime_posix_time.PosixTimeInNanoseconds(timestamp=timestamp)

  @property
  def change_time(self):
    """dfdatetime.DateTimeValues: change time or None if not available."""
    timestamp = self._fsext_file_entry.get_inode_change_time_as_integer()

    # If creation time is not present (None) the timestamp precision is in
    # seconds.
    if self._creation_time is None:
      timestamp, _ = divmod(timestamp, self._NANOSECONDS_PER_SECOND)
      return dfdatetime_posix_time.PosixTime(timestamp=timestamp)

    return dfdatetime_posix_time.PosixTimeInNanoseconds(timestamp=timestamp)

  @property
  def creation_time(self):
    """dfdatetime.DateTimeValues: creation time or None if not available."""
    # Creation time can be None if not present and 0 if not set.
    if not self._creation_time:
      return None

    return dfdatetime_posix_time.PosixTimeInNanoseconds(
        timestamp=self._creation_time)

  @property
  def deletion_time(self):
    """dfdatetime.DateTimeValues: deletion time or None if not available."""
    timestamp = self._fsext_file_entry.get_deletion_time_as_integer()
    # Deletion time can be 0 if not set.
    if not timestamp:
      return None

    return dfdatetime_posix_time.PosixTime(timestamp=timestamp)

  @property
  def name(self):
    """str: name of the file entry, which does not include the full path."""
    return self._name

  @property
  def modification_time(self):
    """dfdatetime.DateTimeValues: modification time or None if not available."""
    timestamp = self._fsext_file_entry.get_modification_time_as_integer()

    # If creation time is not present (None) the timestamp precision is in
    # seconds.
    if self._creation_time is None:
      timestamp, _ = divmod(timestamp, self._NANOSECONDS_PER_SECOND)
      return dfdatetime_posix_time.PosixTime(timestamp=timestamp)

    return dfdatetime_posix_time.PosixTimeInNanoseconds(timestamp=timestamp)

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    return self._fsext_file_entry.size

  def GetExtents(self):
    """Retrieves the extents.

    Returns:
      list[Extent]: the extents.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_FILE:
      return []

    extents = []
    for extent_index in range(self._fsext_file_entry.number_of_extents):
      extent_offset, extent_size, extent_flags = (
          self._fsext_file_entry.get_extent(extent_index))

      if extent_flags & 0x1:
        extent_type = definitions.EXTENT_TYPE_SPARSE
      else:
        extent_type = definitions.EXTENT_TYPE_DATA

      data_stream_extent = extent.Extent(
          extent_type=extent_type, offset=extent_offset, size=extent_size)
      extents.append(data_stream_extent)

    return extents

  def GetEXTFileEntry(self):
    """Retrieves the EXT file entry.

    Returns:
      pyfsext.file_entry: EXT file entry.
    """
    return self._fsext_file_entry

  def GetLinkedFileEntry(self):
    """Retrieves the linked file entry, e.g. for a symbolic link.

    Returns:
      EXTFileEntry: linked file entry or None if not available.
    """
    link = self._GetLink()
    if not link:
      return None

    parent_path_spec = getattr(self.path_spec, 'parent', None)
    path_spec = ext_path_spec.EXTPathSpec(
        location=link, parent=parent_path_spec)

    is_root = bool(link == self._file_system.LOCATION_ROOT)

    return EXTFileEntry(
        self._resolver_context, self._file_system, path_spec, is_root=is_root)

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      EXTFileEntry: parent file entry or None if not available.
    """
    parent_location = None

    location = getattr(self.path_spec, 'location', None)
    if location is not None:
      parent_location = self._file_system.DirnamePath(location)
      if parent_location == '':
        parent_location = self._file_system.PATH_SEPARATOR

    parent_path_spec = getattr(self.path_spec, 'parent', None)
    path_spec = ext_path_spec.EXTPathSpec(
        location=parent_location, parent=parent_path_spec)

    is_root = bool(parent_location == self._file_system.LOCATION_ROOT)

    return EXTFileEntry(
        self._resolver_context, self._file_system, path_spec, is_root=is_root)
