# -*- coding: utf-8 -*-
"""The TAR file entry implementation."""

from dfdatetime import posix_time as dfdatetime_posix_time

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import tar_path_spec
from dfvfs.vfs import attribute
from dfvfs.vfs import file_entry
from dfvfs.vfs import tar_directory


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
    elif self._tar_info.ischr():
      self.entry_type = definitions.FILE_ENTRY_TYPE_CHARACTER_DEVICE
    elif self._tar_info.isblk():
      self.entry_type = definitions.FILE_ENTRY_TYPE_BLOCK_DEVICE
    elif self._tar_info.isfifo():
      self.entry_type = definitions.FILE_ENTRY_TYPE_PIPE

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      TARDirectory: a directory.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return None

    return tar_directory.TARDirectory(self._file_system, self.path_spec)

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

  def _GetStatAttribute(self):
    """Retrieves a stat attribute.

    Returns:
      StatAttribute: a stat attribute or None if not available.
    """
    stat_attribute = attribute.StatAttribute()
    stat_attribute.group_identifier = getattr(self._tar_info, 'gid', None)
    stat_attribute.mode = getattr(self._tar_info, 'mode', None)
    stat_attribute.owner_identifier = getattr(self._tar_info, 'uid', None)
    stat_attribute.size = getattr(self._tar_info, 'size', None)
    stat_attribute.type = self.entry_type

    return stat_attribute

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      TARFileEntry: a sub file entry.
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      tar_file = self._file_system.GetTARFile()
      if tar_file:
        for path_spec in self._directory.entries:
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
