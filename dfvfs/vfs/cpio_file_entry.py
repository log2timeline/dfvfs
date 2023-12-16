# -*- coding: utf-8 -*-
"""The CPIO file entry implementation."""

import stat

from dfdatetime import posix_time as dfdatetime_posix_time

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import cpio_path_spec
from dfvfs.vfs import attribute
from dfvfs.vfs import cpio_directory
from dfvfs.vfs import file_entry


class CPIOFileEntry(file_entry.FileEntry):
  """File system file entry that uses CPIOArchiveFile."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_CPIO

  def __init__(
      self, resolver_context, file_system, path_spec,
      cpio_archive_file_entry=None, is_root=False, is_virtual=False):
    """Initializes a file entry object.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      cpio_archive_file_entry (Optional[CPIOArchiveFileEntry]): CPIO archive
          file entry.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
          entry emulated by the corresponding file system.

    Raises:
      BackEndError: when the CPIO archive file entry is missing in
          a non-virtual file entry.
    """
    if not is_virtual and cpio_archive_file_entry is None:
      cpio_archive_file_entry = file_system.GetCPIOArchiveFileEntryByPathSpec(
          path_spec)
    if not is_virtual and cpio_archive_file_entry is None:
      raise errors.BackEndError(
          'Missing CPIO archive file entry in non-virtual file entry.')

    super(CPIOFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._cpio_archive_file_entry = cpio_archive_file_entry

    # The stat info member st_mode can have multiple types e.g.
    # LINK and DIRECTORY in case of a symbolic link to a directory
    # dfVFS currently only supports one type so we need to check
    # for LINK first.
    mode = getattr(cpio_archive_file_entry, 'mode', 0)
    if stat.S_ISLNK(mode):
      self.entry_type = definitions.FILE_ENTRY_TYPE_LINK
    # The root file entry is virtual and should have type directory.
    elif is_virtual or stat.S_ISDIR(mode):
      self.entry_type = definitions.FILE_ENTRY_TYPE_DIRECTORY
    elif stat.S_ISREG(mode):
      self.entry_type = definitions.FILE_ENTRY_TYPE_FILE
    elif stat.S_ISCHR(mode):
      self.entry_type = definitions.FILE_ENTRY_TYPE_CHARACTER_DEVICE
    elif stat.S_ISBLK(mode):
      self.entry_type = definitions.FILE_ENTRY_TYPE_BLOCK_DEVICE
    elif stat.S_ISFIFO(mode):
      self.entry_type = definitions.FILE_ENTRY_TYPE_PIPE
    elif stat.S_ISSOCK(mode):
      self.entry_type = definitions.FILE_ENTRY_TYPE_SOCKET

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      CPIODirectory: a directory.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return None

    return cpio_directory.CPIODirectory(self._file_system, self.path_spec)

  def _GetLink(self):
    """Retrieves the link.

    Returns:
      str: full path of the linked file entry.
    """
    if self._link is None:
      cpio_archive_file = self._file_system.GetCPIOArchiveFile()
      link_data = cpio_archive_file.ReadDataAtOffset(
          self._cpio_archive_file_entry.data_offset,
          self._cpio_archive_file_entry.data_size)

      self._link = link_data.decode(cpio_archive_file.encoding)

    return self._link

  def _GetStatAttribute(self):
    """Retrieves a stat attribute.

    Returns:
      StatAttribute: a stat attribute or None if not available.
    """
    mode = getattr(self._cpio_archive_file_entry, 'mode', 0)

    stat_attribute = attribute.StatAttribute()
    stat_attribute.group_identifier = getattr(
        self._cpio_archive_file_entry, 'group_identifier', None)
    stat_attribute.inode_number = getattr(
        self._cpio_archive_file_entry, 'inode_number', None)
    stat_attribute.mode = stat.S_IMODE(mode)
    stat_attribute.number_of_links = getattr(
        self._cpio_archive_file_entry, 'number_of_links', None)
    stat_attribute.owner_identifier = getattr(
        self._cpio_archive_file_entry, 'user_identifier', None)
    stat_attribute.size = getattr(
        self._cpio_archive_file_entry, 'data_size', None)
    stat_attribute.type = self.entry_type

    return stat_attribute

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      CPIOFileEntry: a sub file entry.
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        cpio_archive_file_entry = (
            self._file_system.GetCPIOArchiveFileEntryByPathSpec(path_spec))
        is_virtual = not bool(cpio_archive_file_entry)

        yield CPIOFileEntry(
            self._resolver_context, self._file_system, path_spec,
            is_virtual=is_virtual)

  @property
  def name(self):
    """str: name of the file entry, which does not include the full path."""
    # Note that the root file entry is virtual and has no
    # cpio_archive_file_entry.
    if self._cpio_archive_file_entry is None:
      return ''

    return self._file_system.BasenamePath(self._cpio_archive_file_entry.path)

  @property
  def modification_time(self):
    """dfdatetime.DateTimeValues: modification time or None if not available."""
    timestamp = getattr(
        self._cpio_archive_file_entry, 'modification_time', None)
    if timestamp is None:
      return None
    return dfdatetime_posix_time.PosixTime(timestamp=timestamp)

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    return getattr(self._cpio_archive_file_entry, 'data_size', None)

  def GetCPIOArchiveFileEntry(self):
    """Retrieves the CPIO archive file entry object.

    Returns:
      CPIOArchiveFileEntry: CPIO archive file entry.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """
    return self._cpio_archive_file_entry

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      CPIOFileEntry: parent file entry or None if not available.
    """
    location = getattr(self.path_spec, 'location', None)
    if location is None:
      return None

    parent_location = self._file_system.DirnamePath(location)
    if parent_location is None:
      return None

    if parent_location == '':
      parent_location = self._file_system.PATH_SEPARATOR
      is_root = True
      is_virtual = True
    else:
      is_root = False
      is_virtual = False

    parent_path_spec = getattr(self.path_spec, 'parent', None)
    path_spec = cpio_path_spec.CPIOPathSpec(
        location=parent_location, parent=parent_path_spec)
    return CPIOFileEntry(
        self._resolver_context, self._file_system, path_spec,
        is_root=is_root, is_virtual=is_virtual)
