# -*- coding: utf-8 -*-
"""The APFS file entry implementation."""

from __future__ import unicode_literals

from dfdatetime import apfs_time as dfdatetime_apfs_time

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import apfs_path_spec
from dfvfs.vfs import file_entry


class APFSDirectory(file_entry.Directory):
  """File system directory that uses pyfsapfs."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      APFSPathSpec: APFS path specification.
    """
    try:
      fsapfs_file_entry = self._file_system.GetAPFSFileEntryByPathSpec(
          self.path_spec)
    except errors.PathSpecError:
      return

    location = getattr(self.path_spec, 'location', None)

    for fsapfs_sub_file_entry in fsapfs_file_entry.sub_file_entries:
      directory_entry = fsapfs_sub_file_entry.name

      if not location or location == self._file_system.PATH_SEPARATOR:
        directory_entry = self._file_system.JoinPath([directory_entry])
      else:
        directory_entry = self._file_system.JoinPath([
            location, directory_entry])

      yield apfs_path_spec.APFSPathSpec(
          identifier=fsapfs_sub_file_entry.identifier, location=directory_entry,
          parent=self.path_spec.parent)


class APFSFileEntry(file_entry.FileEntry):
  """File system file entry that uses pyfsapfs."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_APFS

  # Mappings of APFS file types to dfVFS file entry types.
  _ENTRY_TYPES = {
      0x1000: definitions.FILE_ENTRY_TYPE_PIPE,
      0x2000: definitions.FILE_ENTRY_TYPE_DEVICE,
      0x4000: definitions.FILE_ENTRY_TYPE_DIRECTORY,
      0x6000: definitions.FILE_ENTRY_TYPE_DEVICE,
      0x8000: definitions.FILE_ENTRY_TYPE_FILE,
      0xa000: definitions.FILE_ENTRY_TYPE_LINK,
      0xc000: definitions.FILE_ENTRY_TYPE_SOCKET,
      0xe000: definitions.FILE_ENTRY_TYPE_WHITEOUT}

  def __init__(
      self, resolver_context, file_system, path_spec, fsapfs_file_entry=None,
      is_root=False, is_virtual=False):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      fsapfs_file_entry (Optional[pyfsapfs.file_entry]): APFS file entry.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
          entry emulated by the corresponding file system.

    Raises:
      BackEndError: if the pyfsapfs file entry is missing.
    """
    if not fsapfs_file_entry:
      fsapfs_file_entry = file_system.GetAPFSFileEntryByPathSpec(path_spec)
    if not fsapfs_file_entry:
      raise errors.BackEndError('Missing pyfsapfs file entry.')

    super(APFSFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._fsapfs_file_entry = fsapfs_file_entry

    self.entry_type = self._ENTRY_TYPES.get(
        fsapfs_file_entry.file_mode & 0xf000, None)

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      APFSDirectory: a directory.
    """
    if self._directory is None:
      self._directory = APFSDirectory(self._file_system, self.path_spec)

    return self._directory

  def _GetLink(self):
    """Retrieves the link.

    Returns:
      str: path of the linked file.
    """
    if self._link is None:
      self._link = self._fsapfs_file_entry.symbolic_link_target
      if self._link and self._link[0] != self._file_system.PATH_SEPARATOR:
        # TODO: make link absolute.
        self._link = '/{0:s}'.format(self._link)

    return self._link

  def _GetStat(self):
    """Retrieves information about the file entry.

    Returns:
      VFSStat: a stat object.
    """
    stat_object = super(APFSFileEntry, self)._GetStat()

    # Ownership and permissions stat information.
    stat_object.mode = self._fsapfs_file_entry.file_mode & 0x0fff
    stat_object.uid = self._fsapfs_file_entry.owner_identifier
    stat_object.gid = self._fsapfs_file_entry.group_identifier

    # Other stat information.
    stat_object.ino = self._fsapfs_file_entry.identifier
    stat_object.fs_type = 'APFS'

    return stat_object

  def _GetSubFileEntries(self):
    """Retrieves a sub file entries generator.

    Yields:
      APFSFileEntry: a sub file entry.
    """
    if self.entry_type == definitions.FILE_ENTRY_TYPE_DIRECTORY:
      directory = self._GetDirectory()
      for path_spec in directory.entries:
        yield APFSFileEntry(
            self._resolver_context, self._file_system, path_spec)

  @property
  def access_time(self):
    """dfdatetime.DateTimeValues: access time or None if not available."""
    timestamp = self._fsapfs_file_entry.get_access_time_as_integer()
    return dfdatetime_apfs_time.APFSTime(timestamp=timestamp)

  @property
  def added_time(self):
    """dfdatetime.DateTimeValues: added time or None if not available."""
    timestamp = self._fsapfs_file_entry.get_added_time_as_integer()
    if timestamp is None:
      return None

    return dfdatetime_apfs_time.APFSTime(timestamp=timestamp)

  @property
  def change_time(self):
    """dfdatetime.DateTimeValues: change time or None if not available."""
    timestamp = self._fsapfs_file_entry.get_inode_change_time_as_integer()
    return dfdatetime_apfs_time.APFSTime(timestamp=timestamp)

  @property
  def creation_time(self):
    """dfdatetime.DateTimeValues: creation time or None if not available."""
    timestamp = self._fsapfs_file_entry.get_creation_time_as_integer()
    return dfdatetime_apfs_time.APFSTime(timestamp=timestamp)

  @property
  def modification_time(self):
    """dfdatetime.DateTimeValues: modification time or None if not available."""
    timestamp = self._fsapfs_file_entry.get_modification_time_as_integer()
    return dfdatetime_apfs_time.APFSTime(timestamp=timestamp)

  @property
  def name(self):
    """str: name of the file entry, which does not include the full path."""
    # The root directory file name is typically 'root', dfVFS however uses ''.
    if self._is_root:
      return ''

    return self._fsapfs_file_entry.name

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    return self._fsapfs_file_entry.size

  def GetAPFSFileEntry(self):
    """Retrieves the APFS file entry.

    Returns:
      pyfsapfs.file_entry: APFS file entry.
    """
    return self._fsapfs_file_entry

  def GetLinkedFileEntry(self):
    """Retrieves the linked file entry, e.g. for a symbolic link.

    Returns:
      APFSFileEntry: linked file entry or None if not available.
    """
    link = self._GetLink()
    if not link:
      return None

    # TODO: is there a way to determine the identifier here?
    link_identifier = None

    parent_path_spec = getattr(self.path_spec, 'parent', None)
    path_spec = apfs_path_spec.APFSPathSpec(
        location=link, parent=parent_path_spec)

    is_root = bool(
        link == self._file_system.LOCATION_ROOT or
        link_identifier == self._file_system.ROOT_DIRECTORY_IDENTIFIER)

    return APFSFileEntry(
        self._resolver_context, self._file_system, path_spec, is_root=is_root)

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      APFSFileEntry: parent file entry or None if not available.
    """
    parent_location = None

    location = getattr(self.path_spec, 'location', None)
    if location is not None:
      parent_location = self._file_system.DirnamePath(location)
      if parent_location == '':
        parent_location = self._file_system.PATH_SEPARATOR

    parent_identifier = self._fsapfs_file_entry.parent_identifier
    if parent_identifier is None:
      return None

    parent_path_spec = getattr(self.path_spec, 'parent', None)
    path_spec = apfs_path_spec.APFSPathSpec(
        location=parent_location, identifier=parent_identifier,
        parent=parent_path_spec)

    is_root = bool(
        parent_location == self._file_system.LOCATION_ROOT or
        parent_identifier == self._file_system.ROOT_DIRECTORY_IDENTIFIER)

    return APFSFileEntry(
        self._resolver_context, self._file_system, path_spec, is_root=is_root)
