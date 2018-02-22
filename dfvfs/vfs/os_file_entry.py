# -*- coding: utf-8 -*-
"""The operating system file entry implementation."""

from __future__ import unicode_literals

import errno
import os
import platform
import stat

import pysmdev

from dfdatetime import posix_time as dfdatetime_posix_time

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import py2to3
from dfvfs.path import os_path_spec
from dfvfs.vfs import file_entry


class OSDirectory(file_entry.Directory):
  """File system directory that uses os."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      OSPathSpec: a path specification.

    Raises:
      AccessError: if the access to list the directory was denied.
      BackEndError: if the directory could not be listed.
    """
    location = getattr(self.path_spec, 'location', None)
    if location is None:
      return

    # Windows will raise WindowsError, which can be caught by OSError,
    # if the process has not access to list the directory. The os.access()
    # function cannot be used since it will return true even when os.listdir()
    # fails.
    try:
      for directory_entry in os.listdir(location):
        directory_entry_location = self._file_system.JoinPath([
            location, directory_entry])
        yield os_path_spec.OSPathSpec(location=directory_entry_location)

    except OSError as exception:
      if exception.errno == errno.EACCES:
        exception_string = str(exception)
        if not isinstance(exception_string, py2to3.UNICODE_TYPE):
          exception_string = py2to3.UNICODE_TYPE(
              exception_string, errors='replace')

        raise errors.AccessError(
            'Access to directory denied with error: {0:s}'.format(
                exception_string))
      else:
        raise errors.BackEndError(
            'Unable to list directory: {0:s} with error: {1:s}'.format(
                location, exception))


class OSFileEntry(file_entry.FileEntry):
  """File system file entry that uses os."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_OS

  def __init__(self, resolver_context, file_system, path_spec, is_root=False):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.

    Raises:
      BackEndError: If an OSError comes up it is caught and an
          BackEndError error is raised instead.
    """
    location = getattr(path_spec, 'location', None)

    # Windows does not support running os.stat on device files so we use
    # libsmdev to do an initial check.
    is_windows_device = False
    if platform.system() == 'Windows' and location:
      try:
        # pylint: disable=no-member
        is_windows_device = pysmdev.check_device(location)
      except IOError:
        pass

    stat_info = None
    if not is_windows_device and location:
      # We are only catching OSError. However on the Windows platform
      # a WindowsError can be raised as well. We are not catching that since
      # that error does not exist on non-Windows platforms.
      try:
        stat_info = os.lstat(location)
      except OSError as exception:
        raise errors.BackEndError(
            'Unable to retrieve stat object with error: {0!s}'.format(
                exception))

    super(OSFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=False)
    self._is_windows_device = is_windows_device
    self._name = None
    self._stat_info = stat_info

    if is_windows_device:
      self.entry_type = definitions.FILE_ENTRY_TYPE_DEVICE

    elif stat_info:
      # If location contains a trailing segment separator and points to
      # a symbolic link to a directory stat info will not indicate
      # the file entry as a symbolic link. The following check ensures
      # that the LINK type is correctly detected.
      is_link = os.path.islink(location)

      # The stat info member st_mode can have multiple types e.g.
      # LINK and DIRECTORY in case of a symbolic link to a directory
      # dfVFS currently only supports one type so we need to check
      # for LINK first.
      if stat.S_ISLNK(stat_info.st_mode) or is_link:
        self.entry_type = definitions.FILE_ENTRY_TYPE_LINK
      elif stat.S_ISREG(stat_info.st_mode):
        self.entry_type = definitions.FILE_ENTRY_TYPE_FILE
      elif stat.S_ISDIR(stat_info.st_mode):
        self.entry_type = definitions.FILE_ENTRY_TYPE_DIRECTORY
      elif (stat.S_ISCHR(stat_info.st_mode) or
            stat.S_ISBLK(stat_info.st_mode)):
        self.entry_type = definitions.FILE_ENTRY_TYPE_DEVICE
      elif stat.S_ISFIFO(stat_info.st_mode):
        self.entry_type = definitions.FILE_ENTRY_TYPE_PIPE
      elif stat.S_ISSOCK(stat_info.st_mode):
        self.entry_type = definitions.FILE_ENTRY_TYPE_SOCKET

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      OSDirectory: a directory object or None if not available.
    """
    if self.entry_type == definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return OSDirectory(self._file_system, self.path_spec)

  def _GetLink(self):
    """Retrieves the link."""
    if self._link is None:
      self._link = ''

      if not self.IsLink():
        return self._link

      location = getattr(self.path_spec, 'location', None)
      if location is None:
        return self._link

      self._link = os.readlink(location)
      self._link = os.path.abspath(self._link)

    return self._link

  def _GetStat(self):
    """Retrieves information about the file entry.

    Returns:
      VFSStat: a stat object or None if not available.
    """
    stat_object = super(OSFileEntry, self)._GetStat()

    if not self._is_windows_device:
      # File data stat information.
      stat_object.size = self._stat_info.st_size

      # Ownership and permissions stat information.
      stat_object.mode = stat.S_IMODE(self._stat_info.st_mode)
      stat_object.uid = self._stat_info.st_uid
      stat_object.gid = self._stat_info.st_gid

      # Other stat information.
      stat_object.ino = self._stat_info.st_ino
      # stat_info.st_dev
      # stat_info.st_nlink

    return stat_object

  @property
  def access_time(self):
    """dfdatetime.DateTimeValues: access time or None if not available."""
    timestamp = int(self._stat_info.st_atime)
    return dfdatetime_posix_time.PosixTime(timestamp=timestamp)

  @property
  def change_time(self):
    """dfdatetime.DateTimeValues: change time or None if not available."""
    timestamp = int(self._stat_info.st_ctime)
    return dfdatetime_posix_time.PosixTime(timestamp=timestamp)

  @property
  def link(self):
    """str: full path of the linked file entry."""
    if self._link is None:
      self._link = ''

      if not self.IsLink():
        return self._link

      location = getattr(self.path_spec, 'location', None)
      if location is None:
        return self._link

      self._link = os.readlink(location)
      self._link = os.path.abspath(self._link)
    return self._link

  @property
  def name(self):
    """str: name of the file entry, without the full path."""
    if self._name is None:
      location = getattr(self.path_spec, 'location', None)
      if location is not None:
        self._name = self._file_system.BasenamePath(location)
    return self._name

  @property
  def modification_time(self):
    """dfdatetime.DateTimeValues: modification time or None if not available."""
    timestamp = int(self._stat_info.st_mtime)
    return dfdatetime_posix_time.PosixTime(timestamp=timestamp)

  @property
  def sub_file_entries(self):
    """generator[OSFileEntry]: sub file entries."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield OSFileEntry(self._resolver_context, self._file_system, path_spec)

  def GetLinkedFileEntry(self):
    """Retrieves the linked file entry, for example for a symbolic link.

    Retruns:
      OSFileEntry: linked file entry or None if not available.
    """
    link = self._GetLink()
    if not link:
      return

    path_spec = os_path_spec.OSPathSpec(location=link)
    return OSFileEntry(self._resolver_context, self._file_system, path_spec)

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      OSFileEntry: parent file entry or None if not available.
    """
    location = getattr(self.path_spec, 'location', None)
    if location is None:
      return

    parent_location = self._file_system.DirnamePath(location)
    if parent_location is None:
      return

    if parent_location == '':
      parent_location = self._file_system.PATH_SEPARATOR

    path_spec = os_path_spec.OSPathSpec(location=parent_location)
    return OSFileEntry(self._resolver_context, self._file_system, path_spec)
