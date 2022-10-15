# -*- coding: utf-8 -*-
"""The HFS file entry implementation."""

import copy

from dfdatetime import hfs_time as dfdatetime_hfs_time
from dfdatetime import posix_time as dfdatetime_posix_time

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import hfs_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import attribute
from dfvfs.vfs import extent
from dfvfs.vfs import file_entry
from dfvfs.vfs import hfs_attribute
from dfvfs.vfs import hfs_data_stream
from dfvfs.vfs import hfs_directory


class HFSFileEntry(file_entry.FileEntry):
  """File system file entry that uses pyfshfs."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_HFS

  # Mappings of HFS file types to dfVFS file entry types.
  _ENTRY_TYPES = {
      0x1000: definitions.FILE_ENTRY_TYPE_PIPE,
      0x2000: definitions.FILE_ENTRY_TYPE_CHARACTER_DEVICE,
      0x4000: definitions.FILE_ENTRY_TYPE_DIRECTORY,
      0x6000: definitions.FILE_ENTRY_TYPE_BLOCK_DEVICE,
      0x8000: definitions.FILE_ENTRY_TYPE_FILE,
      0xa000: definitions.FILE_ENTRY_TYPE_LINK,
      0xc000: definitions.FILE_ENTRY_TYPE_SOCKET,
      0xe000: definitions.FILE_ENTRY_TYPE_WHITEOUT}

  def __init__(
      self, resolver_context, file_system, path_spec, fshfs_file_entry=None,
      is_root=False, is_virtual=False):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      fshfs_file_entry (Optional[pyfshfs.file_entry]): HFS file entry.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
          entry emulated by the corresponding file system.

    Raises:
      BackEndError: if the pyfshfs file entry is missing.
    """
    if not fshfs_file_entry:
      fshfs_file_entry = file_system.GetHFSFileEntryByPathSpec(path_spec)
    if not fshfs_file_entry:
      raise errors.BackEndError('Missing pyfshfs file entry.')

    if is_root:
      file_entry_name = ''
    else:
      file_entry_name = fshfs_file_entry.name

    super(HFSFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._fshfs_file_entry = fshfs_file_entry
    self._name = file_entry_name

    self.entry_type = self._ENTRY_TYPES.get(
        fshfs_file_entry.file_mode & 0xf000, None)

  def _GetAttributes(self):
    """Retrieves the attributes.

    Returns:
      list[Attribute]: attributes.
    """
    if self._attributes is None:
      self._attributes = []

      for fshfs_extended_attribute in (
          self._fshfs_file_entry.extended_attributes):
        extended_attribute = hfs_attribute.HFSExtendedAttribute(
            fshfs_extended_attribute)
        self._attributes.append(extended_attribute)

    return self._attributes

  def _GetDataStreams(self):
    """Retrieves the data streams.

    Returns:
      list[HFSDataStream]: data streams.
    """
    if self._data_streams is None:
      self._data_streams = []

      if self.entry_type == definitions.FILE_ENTRY_TYPE_FILE:
        data_stream = hfs_data_stream.HFSDataStream(self, None)
        self._data_streams.append(data_stream)

      fshfs_data_stream = self._fshfs_file_entry.get_resource_fork()
      if fshfs_data_stream:
        data_stream = hfs_data_stream.HFSDataStream(self, fshfs_data_stream)
        self._data_streams.append(data_stream)

    return self._data_streams

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      HFSDirectory: directory or None if not available.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return None

    return hfs_directory.HFSDirectory(
        self._file_system, self.path_spec, self._fshfs_file_entry)

  def _GetLink(self):
    """Retrieves the link.

    Returns:
      str: path of the linked file.
    """
    if self._link is None:
      self._link = self._fshfs_file_entry.symbolic_link_target
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
    stat_attribute.device_number = self._fshfs_file_entry.device_number
    stat_attribute.group_identifier = self._fshfs_file_entry.group_identifier
    stat_attribute.inode_number = self._fshfs_file_entry.identifier
    stat_attribute.mode = self._fshfs_file_entry.file_mode
    stat_attribute.number_of_links = self._fshfs_file_entry.number_of_links
    stat_attribute.owner_identifier = self._fshfs_file_entry.owner_identifier
    stat_attribute.size = self._fshfs_file_entry.size
    stat_attribute.type = self.entry_type

    return stat_attribute

  def _GetSubFileEntries(self):
    """Retrieves a sub file entries generator.

    Yields:
      HFSFileEntry: a sub file entry.
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield HFSFileEntry(self._resolver_context, self._file_system, path_spec)

  @property
  def access_time(self):
    """dfdatetime.DateTimeValues: access time or None if not available."""
    timestamp = self._fshfs_file_entry.get_access_time_as_integer()
    if timestamp is None:
      return None

    return dfdatetime_hfs_time.HFSTime(timestamp=timestamp)

  @property
  def added_time(self):
    """dfdatetime.DateTimeValues: added time or None if not available."""
    timestamp = self._fshfs_file_entry.get_added_time_as_integer()
    if timestamp is None:
      return None

    return dfdatetime_posix_time.PosixTime(timestamp=timestamp)

  @property
  def backup_time(self):
    """dfdatetime.DateTimeValues: backup time or None if not available."""
    timestamp = self._fshfs_file_entry.get_backup_time_as_integer()
    return dfdatetime_hfs_time.HFSTime(timestamp=timestamp)

  @property
  def change_time(self):
    """dfdatetime.DateTimeValues: change time or None if not available."""
    timestamp = self._fshfs_file_entry.get_entry_modification_time_as_integer()
    if timestamp is None:
      return None

    return dfdatetime_hfs_time.HFSTime(timestamp=timestamp)

  @property
  def creation_time(self):
    """dfdatetime.DateTimeValues: creation time or None if not available."""
    timestamp = self._fshfs_file_entry.get_creation_time_as_integer()
    return dfdatetime_hfs_time.HFSTime(timestamp=timestamp)

  @property
  def name(self):
    """str: name of the file entry, which does not include the full path."""
    return self._name

  @property
  def modification_time(self):
    """dfdatetime.DateTimeValues: modification time or None if not available."""
    timestamp = self._fshfs_file_entry.get_modification_time_as_integer()
    return dfdatetime_hfs_time.HFSTime(timestamp=timestamp)

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    return self._fshfs_file_entry.size

  def GetExtents(self):
    """Retrieves the extents.

    Returns:
      list[Extent]: the extents.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_FILE:
      return []

    extents = []
    for extent_index in range(self._fshfs_file_entry.number_of_extents):
      extent_offset, extent_size, extent_flags = (
          self._fshfs_file_entry.get_extent(extent_index))

      if extent_flags & 0x1:
        extent_type = definitions.EXTENT_TYPE_SPARSE
      else:
        extent_type = definitions.EXTENT_TYPE_DATA

      data_stream_extent = extent.Extent(
          extent_type=extent_type, offset=extent_offset, size=extent_size)
      extents.append(data_stream_extent)

    return extents

  def GetFileObject(self, data_stream_name=''):
    """Retrieves a file-like object of a specific data stream.

    Args:
      data_stream_name (Optional[str]): name of the data stream, where an empty
          string represents the default data stream.

    Returns:
      FileIO: a file-like object or None if not available.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_FILE or (
        data_stream_name and data_stream_name != 'rsrc'):
      return None

    # Make sure to make the changes on a copy of the path specification, so we
    # do not alter self.path_spec.
    path_spec = copy.deepcopy(self.path_spec)
    if data_stream_name:
      setattr(path_spec, 'data_stream', data_stream_name)

    return resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=self._resolver_context)

  def GetHFSFileEntry(self):
    """Retrieves the HFS file entry.

    Returns:
      pyfshfs.file_entry: HFS file entry.
    """
    return self._fshfs_file_entry

  def GetLinkedFileEntry(self):
    """Retrieves the linked file entry, e.g. for a symbolic link.

    Returns:
      HFSFileEntry: linked file entry or None if not available.
    """
    link = self._GetLink()
    if not link:
      return None

    parent_path_spec = getattr(self.path_spec, 'parent', None)
    path_spec = hfs_path_spec.HFSPathSpec(
        location=link, parent=parent_path_spec)

    is_root = bool(link == self._file_system.LOCATION_ROOT)

    return HFSFileEntry(
        self._resolver_context, self._file_system, path_spec, is_root=is_root)

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      HFSFileEntry: parent file entry or None if not available.
    """
    parent_location = None

    location = getattr(self.path_spec, 'location', None)
    if location is not None:
      parent_location = self._file_system.DirnamePath(location)
      if parent_location == '':
        parent_location = self._file_system.PATH_SEPARATOR

    parent_path_spec = getattr(self.path_spec, 'parent', None)
    path_spec = hfs_path_spec.HFSPathSpec(
        location=parent_location, parent=parent_path_spec)

    is_root = bool(parent_location == self._file_system.LOCATION_ROOT)

    return HFSFileEntry(
        self._resolver_context, self._file_system, path_spec, is_root=is_root)
