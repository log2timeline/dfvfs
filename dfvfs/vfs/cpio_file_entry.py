# -*- coding: utf-8 -*-
"""The CPIO file entry implementation."""

from __future__ import unicode_literals

import stat

from dfdatetime import posix_time as dfdatetime_posix_time

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import cpio_path_spec
from dfvfs.vfs import file_entry


class CPIODirectory(file_entry.Directory):
  """File system directory that uses CPIOArchiveFile."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      CPIOPathSpec: path specification.
    """
    location = getattr(self.path_spec, 'location', None)

    if location and location.startswith(self._file_system.PATH_SEPARATOR):
      cpio_archive_file = self._file_system.GetCPIOArchiveFile()
      for cpio_archive_file_entry in cpio_archive_file.GetFileEntries(
          path_prefix=location[1:]):

        path = cpio_archive_file_entry.path
        if not path:
          continue

        _, suffix = self._file_system.GetPathSegmentAndSuffix(
            location[1:], path)

        # Ignore anything that is part of a sub directory or the directory
        # itself.
        if suffix or path == location:
          continue

        path_spec_location = self._file_system.JoinPath([path])
        yield cpio_path_spec.CPIOPathSpec(
            location=path_spec_location, parent=self.path_spec.parent)


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
    elif stat.S_ISCHR(mode) or stat.S_ISBLK(mode):
      self.entry_type = definitions.FILE_ENTRY_TYPE_DEVICE
    elif stat.S_ISFIFO(mode):
      self.entry_type = definitions.FILE_ENTRY_TYPE_PIPE
    elif stat.S_ISSOCK(mode):
      self.entry_type = definitions.FILE_ENTRY_TYPE_SOCKET

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      CPIODirectory: a directory.
    """
    if self._directory is None:
      self._directory = CPIODirectory(self._file_system, self.path_spec)

    return self._directory

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

      # TODO: should this be ASCII?
      self._link = link_data.decode('ascii')

    return self._link

  def _GetStat(self):
    """Retrieves information about the file entry.

    Returns:
      VFSStat: a stat object.
    """
    stat_object = super(CPIOFileEntry, self)._GetStat()

    # Ownership and permissions stat information.
    mode = getattr(self._cpio_archive_file_entry, 'mode', 0)
    stat_object.mode = stat.S_IMODE(mode)
    stat_object.uid = getattr(
        self._cpio_archive_file_entry, 'user_identifier', None)
    stat_object.gid = getattr(
        self._cpio_archive_file_entry, 'group_identifier', None)

    return stat_object

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      CPIOFileEntry: a sub file entry.
    """
    if self.entry_type == definitions.FILE_ENTRY_TYPE_DIRECTORY:
      directory = self._GetDirectory()
      for path_spec in directory.entries:
        yield CPIOFileEntry(
            self._resolver_context, self._file_system, path_spec)

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
