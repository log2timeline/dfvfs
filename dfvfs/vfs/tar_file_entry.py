# -*- coding: utf-8 -*-
"""The TAR file entry implementation."""

from __future__ import unicode_literals

from dfdatetime import posix_time as dfdatetime_posix_time

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import tar_path_spec
from dfvfs.vfs import file_entry


class TARDirectory(file_entry.Directory):
  """File system directory that uses tarfile."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      TARPathSpec: TAR path specification.
    """
    location = getattr(self.path_spec, 'location', None)

    if location and location.startswith(self._file_system.PATH_SEPARATOR):
      # The TAR info name does not have the leading path separator as
      # the location string does.
      tar_path = location[1:]

      # Set of top level sub directories that have been yielded.
      processed_directories = set()

      tar_file = self._file_system.GetTARFile()
      for tar_info in tar_file.getmembers():
        path = tar_info.name

        # Determine if the start of the TAR info name is similar to
        # the location string. If not the file TAR info refers to is not in
        # the same directory.
        if not path or not path.startswith(tar_path):
          continue

        # Ignore the directory itself.
        if path == tar_path:
          continue

        path_segment, suffix = self._file_system.GetPathSegmentAndSuffix(
            tar_path, path)
        if not path_segment:
          continue

        # Sometimes the TAR file lacks directories, therefore we will
        # provide virtual ones.
        if suffix:
          path_spec_location = self._file_system.JoinPath([
              location, path_segment])
          is_directory = True

        else:
          path_spec_location = self._file_system.JoinPath([path])
          is_directory = tar_info.isdir()

        if is_directory:
          if path_spec_location in processed_directories:
            continue
          processed_directories.add(path_spec_location)

        yield tar_path_spec.TARPathSpec(
            location=path_spec_location, parent=self.path_spec.parent)


class TARFileEntry(file_entry.FileEntry):
  """File system file entry that uses tarfile."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TAR

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False, tar_info=None):
    """Initializes the file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
          entry emulated by the corresponding file system.
      tar_info (Optional[tarfile.TARInfo]): TAR info.

    Raises:
      BackEndError: when the TAR info is missing in a non-virtual file entry.
    """
    if not is_virtual and tar_info is None:
      tar_info = file_system.GetTARInfoByPathSpec(path_spec)
    if not is_virtual and tar_info is None:
      raise errors.BackEndError('Missing TAR info in non-virtual file entry.')

    super(TARFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._tar_info = tar_info

    if self._is_virtual or self._tar_info.isdir():
      self.entry_type = definitions.FILE_ENTRY_TYPE_DIRECTORY
    elif self._tar_info.isfile():
      self.entry_type = definitions.FILE_ENTRY_TYPE_FILE
    elif self._tar_info.issym() or self._tar_info.islnk():
      self.entry_type = definitions.FILE_ENTRY_TYPE_LINK
    elif self._tar_info.ischr() or self._tar_info.isblk():
      self.entry_type = definitions.FILE_ENTRY_TYPE_DEVICE
    elif self._tar_info.isfifo():
      self.entry_type = definitions.FILE_ENTRY_TYPE_PIPE

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      TARDirectory: a directory.
    """
    if self._directory is None:
      self._directory = TARDirectory(self._file_system, self.path_spec)

    return self._directory

  def _GetLink(self):
    """Retrieves the link.

    Returns:
      str: link.
    """
    if self._link is None:
      self._link = ''
      if self._tar_info:
        self._link = self._tar_info.linkname

    return self._link

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      VFSStat: stat object.
    """
    stat_object = super(TARFileEntry, self)._GetStat()

    # Ownership and permissions stat information.
    stat_object.mode = getattr(self._tar_info, 'mode', None)
    stat_object.uid = getattr(self._tar_info, 'uid', None)
    stat_object.gid = getattr(self._tar_info, 'gid', None)

    return stat_object

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      TARFileEntry: a sub file entry.
    """
    if self.entry_type == definitions.FILE_ENTRY_TYPE_DIRECTORY:
      tar_file = self._file_system.GetTARFile()
      if tar_file:
        directory = self._GetDirectory()
        for path_spec in directory.entries:
          location = getattr(path_spec, 'location', None)
          if location is None:
            continue

          kwargs = {}
          try:
            kwargs['tar_info'] = tar_file.getmember(location[1:])
          except KeyError:
            kwargs['is_virtual'] = True

          yield TARFileEntry(
              self._resolver_context, self._file_system, path_spec, **kwargs)

  @property
  def modification_time(self):
    """dfdatetime.DateTimeValues: modification time or None if not available."""
    timestamp = getattr(self._tar_info, 'mtime', None)
    if timestamp is None:
      return None
    return dfdatetime_posix_time.PosixTime(timestamp=timestamp)

  @property
  def name(self):
    """str: name of the file entry, which does not include the full path."""
    path = getattr(self.path_spec, 'location', None)
    if path is not None and not isinstance(path, str):
      try:
        path = path.decode(self._file_system.encoding)
      except UnicodeDecodeError:
        path = None

    return self._file_system.BasenamePath(path)

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    return getattr(self._tar_info, 'size', None)

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      TARFileEntry: parent file entry or None.
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
    path_spec = tar_path_spec.TARPathSpec(
        location=parent_location, parent=parent_path_spec)
    return TARFileEntry(
        self._resolver_context, self._file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)

  def GetTARInfo(self):
    """Retrieves the TAR info.

    Returns:
      tarfile.TARInfo: TAR info or None if it does not exist.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """
    if not self._tar_info:
      location = getattr(self.path_spec, 'location', None)
      if location is None:
        raise errors.PathSpecError('Path specification missing location.')

      if not location.startswith(self._file_system.LOCATION_ROOT):
        raise errors.PathSpecError('Invalid location in path specification.')

      if len(location) == 1:
        return None

      tar_file = self._file_system.GetTARFile()
      try:
        self._tar_info = tar_file.getmember(location[1:])
      except KeyError:
        pass

    return self._tar_info
