# -*- coding: utf-8 -*-
"""The CPIO file entry implementation."""

import stat

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import cpio_path_spec
from dfvfs.vfs import file_entry
from dfvfs.vfs import vfs_stat


class CPIODirectory(file_entry.Directory):
  """Class that implements a directory object using CPIOArchiveFile."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      A path specification (instance of path.CPIOPathSpec).
    """
    location = getattr(self.path_spec, u'location', None)

    if (location is None or
        not location.startswith(self._file_system.PATH_SEPARATOR)):
      return

    cpio_archive_file = self._file_system.GetCPIOArchiveFile()
    for cpio_archive_file_entry in cpio_archive_file.GetFileEntries(
        path_prefix=location[1:]):

      path = cpio_archive_file_entry.path
      if not path:
        continue

      _, suffix = self._file_system.GetPathSegmentAndSuffix(location[1:], path)

      # Ignore anything that is part of a sub directory or the directory itself.
      if suffix or path == location:
        continue

      path_spec_location = self._file_system.JoinPath([path])
      yield cpio_path_spec.CPIOPathSpec(
          location=path_spec_location, parent=self.path_spec.parent)


class CPIOFileEntry(file_entry.FileEntry):
  """Class that implements a file entry object using CPIOArchiveFile."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_CPIO

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False, cpio_archive_file_entry=None):
    """Initializes the file entry object.
    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      file_system: the file system object (instance of FileSystem).
      path_spec: the path specification (instance of PathSpec).
      is_root: optional boolean value to indicate if the file entry is
               the root file entry of the corresponding file system.
      is_virtual: optional boolean value to indicate if the file entry is
                  a virtual file entry emulated by the corresponding file
                  system.
      cpio_archive_file_entry: optional CPIO archive file entry object
                               (instance of cpio.CPIOArchiveFileEntry).
    """
    super(CPIOFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._cpio_archive_file_entry = cpio_archive_file_entry

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      A directory object (instance of Directory) or None.
    """
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if (self._stat_object and
        self._stat_object.type == self._stat_object.TYPE_DIRECTORY):
      return CPIODirectory(self._file_system, self.path_spec)
    return

  def _GetLink(self):
    """Retrieves the link.

    Raises:
      BackEndError: when the CPIO archive file entry is missing in
                    a non-virtual file entry.
    """
    if self._link is None:
      cpio_archive_file_entry = self.GetCPIOArchiveFileEntry()
      if not self._is_virtual and cpio_archive_file_entry is None:
        raise errors.BackEndError(
            u'Missing CPIO archive file entry in non-virtual file entry.')

      self._link = u''
      if stat.S_ISLNK(cpio_archive_file_entry.mode):
        cpio_archive_file = self._file_system.GetCPIOArchiveFile()
        link_data = cpio_archive_file.ReadDataAtOffset(
            cpio_archive_file_entry.data_offset,
            cpio_archive_file_entry.data_size)

        # TODO: should this be ASCII?
        self._link = link_data.decode(u'ascii')

    return self._link

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of vfs.VFSStat).

    Raises:
      BackEndError: when the CPIO archive file entry is missing in
                    a non-virtual file entry.
    """
    cpio_archive_file_entry = self.GetCPIOArchiveFileEntry()
    if not self._is_virtual and cpio_archive_file_entry is None:
      raise errors.BackEndError(
          u'Missing CPIO archive file entry in non-virtual file entry.')

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    stat_object.size = getattr(cpio_archive_file_entry, u'data_size', None)

    # Date and time stat information.
    stat_object.mtime = getattr(
        cpio_archive_file_entry, u'modification_time', None)

    # Ownership and permissions stat information.
    mode = getattr(cpio_archive_file_entry, u'mode', 0)
    stat_object.mode = stat.S_IMODE(mode)
    stat_object.uid = getattr(
        cpio_archive_file_entry, u'user_identifier', None)
    stat_object.gid = getattr(
        cpio_archive_file_entry, u'group_identifier', None)

    # File entry type stat information.

    # The stat info member st_mode can have multiple types e.g.
    # LINK and DIRECTORY in case of a symbolic link to a directory
    # dfVFS currently only supports one type so we need to check
    # for LINK first.
    if stat.S_ISLNK(mode):
      stat_object.type = stat_object.TYPE_LINK
    # The root file entry is virtual and should have type directory.
    elif self._is_virtual or stat.S_ISDIR(mode):
      stat_object.type = stat_object.TYPE_DIRECTORY
    elif stat.S_ISREG(mode):
      stat_object.type = stat_object.TYPE_FILE
    elif stat.S_ISCHR(mode) or stat.S_ISBLK(mode):
      stat_object.type = stat_object.TYPE_DEVICE
    elif stat.S_ISFIFO(mode):
      stat_object.type = stat_object.TYPE_PIPE
    elif stat.S_ISSOCK(mode):
      stat_object.type = stat_object.TYPE_SOCKET

    return stat_object

  @property
  def name(self):
    """The name of the file entry, which does not include the full path."""
    cpio_archive_file_entry = self.GetCPIOArchiveFileEntry()

    # Note that the root file entry is virtual and has no
    # cpio_archive_file_entry.
    if cpio_archive_file_entry is None:
      return u''

    return self._file_system.BasenamePath(cpio_archive_file_entry.path)

  @property
  def sub_file_entries(self):
    """The sub file entries (generator of instance of vfs.FileEntry)."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield CPIOFileEntry(
            self._resolver_context, self._file_system, path_spec)

  def GetCPIOArchiveFileEntry(self):
    """Retrieves the CPIO archive file entry object.

    Returns:
      The CPIO archive file entry object (instance of
      cpio.CPIOArchiveFileEntry).

    Raises:
      ValueError: if the path specification is incorrect.
    """
    if not self._cpio_archive_file_entry:
      location = getattr(self.path_spec, u'location', None)
      if location is None:
        raise ValueError(u'Path specification missing location.')

      if not location.startswith(self._file_system.LOCATION_ROOT):
        raise ValueError(u'Invalid location in path specification.')

      if len(location) == 1:
        return

      cpio_archive_file = self._file_system.GetCPIOArchiveFile()
      self._cpio_archive_file_entry = cpio_archive_file.GetFileEntryByPath(
          location[1:])

    return self._cpio_archive_file_entry

  def GetParentFileEntry(self):
    """Retrieves the parent file entry."""
    location = getattr(self.path_spec, u'location', None)
    if location is None:
      return

    parent_location = self._file_system.DirnamePath(location)
    if parent_location is None:
      return
    if parent_location == u'':
      parent_location = self._file_system.PATH_SEPARATOR

    parent_path_spec = getattr(self.path_spec, u'parent', None)
    path_spec = cpio_path_spec.CPIOPathSpec(
        location=parent_location, parent=parent_path_spec)
    return CPIOFileEntry(self._resolver_context, self._file_system, path_spec)
