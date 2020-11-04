# -*- coding: utf-8 -*-
"""The HFS file entry implementation."""

from __future__ import unicode_literals

from dfdatetime import hfs_time as dfdatetime_hfs_time
from dfdatetime import posix_time as dfdatetime_posix_time

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import hfs_path_spec
from dfvfs.vfs import file_entry


class HFSDirectory(file_entry.Directory):
  """File system directory that uses pyfshfs."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      HFSPathSpec: HFS path specification.
    """
    try:
      fshfs_file_entry = self._file_system.GetHFSFileEntryByPathSpec(
          self.path_spec)
    except errors.PathSpecError:
      return

    location = getattr(self.path_spec, 'location', None)

    for fshfs_sub_file_entry in fshfs_file_entry.sub_file_entries:
      directory_entry = fshfs_sub_file_entry.name

      if not location or location == self._file_system.PATH_SEPARATOR:
        directory_entry = self._file_system.JoinPath([directory_entry])
      else:
        directory_entry = self._file_system.JoinPath([
            location, directory_entry])

      yield hfs_path_spec.HFSPathSpec(
          identifier=fshfs_sub_file_entry.identifier, location=directory_entry,
          parent=self.path_spec.parent)


class HFSFileEntry(file_entry.FileEntry):
  """File system file entry that uses pyfshfs."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_HFS

  # Mappings of HFS file types to dfVFS file entry types.
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

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      HFSDirectory: directory or None if not available.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return None

    return HFSDirectory(self._file_system, self.path_spec)

  def _GetLink(self):
    """Retrieves the link.

    Returns:
      str: path of the linked file.
    """
    if self._link is None:
      self._link = self._fshfs_file_entry.symbolic_link_target
      if self._link and self._link[0] != self._file_system.PATH_SEPARATOR:
        # TODO: make link absolute.
        self._link = '/{0:s}'.format(self._link)

    return self._link

  def _GetStat(self):
    """Retrieves information about the file entry.

    Returns:
      VFSStat: a stat object.
    """
    stat_object = super(HFSFileEntry, self)._GetStat()

    # File data stat information.
    stat_object.size = self._fshfs_file_entry.size

    # Ownership and permissions stat information.
    stat_object.mode = self._fshfs_file_entry.file_mode & 0x0fff
    stat_object.uid = self._fshfs_file_entry.owner_identifier
    stat_object.gid = self._fshfs_file_entry.group_identifier

    # File entry type stat information.
    stat_object.type = self.entry_type

    # Other stat information.
    stat_object.ino = self._fshfs_file_entry.identifier
    stat_object.fs_type = 'HFS'

    stat_object.is_allocated = True

    return stat_object

  def _GetSubFileEntries(self):
    """Retrieves a sub file entries generator.

    Yields:
      HFSFileEntry: a sub file entry.
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield HFSFileEntry(
            self._resolver_context, self._file_system, path_spec)

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
