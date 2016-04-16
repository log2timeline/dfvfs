# -*- coding: utf-8 -*-
"""The operating system file entry implementation."""

import errno
import os
import platform
import stat

import pysmdev

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import py2to3
from dfvfs.path import os_path_spec
from dfvfs.vfs import file_entry
from dfvfs.vfs import vfs_stat


class OSDirectory(file_entry.Directory):
  """Class that implements an operating system directory object."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      A path specification (instance of path.OSPathSpec).

    Raises:
      AccessError: if the access to list the directory was denied.
      BackEndError: if the directory could not be listed.
    """
    location = getattr(self.path_spec, u'location', None)
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
              exception_string, errors=u'replace')

        raise errors.AccessError(
            u'Access to directory denied with error: {0:s}'.format(
                exception_string))
      else:
        raise errors.BackEndError(
            u'Unable to list directory: {0:s} with error: {1:s}'.format(
                location, exception))


class OSFileEntry(file_entry.FileEntry):
  """Class that implements an operating system file entry object."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_OS

  def __init__(self, resolver_context, file_system, path_spec, is_root=False):
    """Initializes the file entry object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      file_system: the file system object (instance of FileSystem).
      path_spec: the path specification object (instance of PathSpec).
      is_root: optional boolean value to indicate if the file entry is
               the root file entry of the corresponding file system.
    """
    super(OSFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=False)
    self._name = None

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      A directory object (instance of Directory) or None.
    """
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if (self._stat_object and
        self._stat_object.type == self._stat_object.TYPE_DIRECTORY):
      return OSDirectory(self._file_system, self.path_spec)
    return

  def _GetLink(self):
    """Retrieves the link."""
    if self._link is None:
      self._link = u''

      if not self.IsLink():
        return self._link

      location = getattr(self.path_spec, 'location', None)
      if location is None:
        return self._link

      self._link = os.readlink(location)
      self._link = os.path.abspath(self._link)

    return self._link

  def _GetStat(self):
    """Retrieves the stat object (instance of vfs.VFSStat).

    Raises:
      BackEndError: If an OSError comes up it is caught and an
                    BackEndError error is raised instead.
    Returns:
      Stat object (instance of VFSStat) or None if no location is set.
    """
    location = getattr(self.path_spec, u'location', None)
    if location is None:
      return

    stat_object = vfs_stat.VFSStat()

    is_windows_device = False
    stat_info = None

    # Windows does not support running os.stat on device files so we use
    # libsmdev to do an initial check.
    if platform.system() == u'Windows':
      try:
        is_windows_device = pysmdev.check_device(location)
      except IOError:
        pass

    if is_windows_device:
      stat_object.type = stat_object.TYPE_DEVICE

    else:
      # We are only catching OSError. However on the Windows platform
      # a WindowsError can be raised as well. We are not catching that since
      # that error does not exist on non-Windows platforms.
      try:
        stat_info = os.stat(location)
      except OSError as exception:
        raise errors.BackEndError(
            u'Unable to retrieve stat object with error: {0:s}'.format(
                exception))

      # File data stat information.
      stat_object.size = stat_info.st_size

      # Date and time stat information.
      stat_object.atime = stat_info.st_atime
      stat_object.ctime = stat_info.st_ctime
      stat_object.mtime = stat_info.st_mtime

      # Ownership and permissions stat information.
      stat_object.mode = stat.S_IMODE(stat_info.st_mode)
      stat_object.uid = stat_info.st_uid
      stat_object.gid = stat_info.st_gid

      # If location contains a trailing segment separator and points to
      # a symbolic link to a directory stat info will not indicate
      # the file entry as a symbolic link. The following check ensures
      # that the LINK type is correctly detected.
      is_link = os.path.islink(location)

      # File entry type stat information.

      # The stat info member st_mode can have multiple types e.g.
      # LINK and DIRECTORY in case of a symbolic link to a directory
      # dfVFS currently only supports one type so we need to check
      # for LINK first.
      if stat.S_ISLNK(stat_info.st_mode) or is_link:
        stat_object.type = stat_object.TYPE_LINK
      elif stat.S_ISREG(stat_info.st_mode):
        stat_object.type = stat_object.TYPE_FILE
      elif stat.S_ISDIR(stat_info.st_mode):
        stat_object.type = stat_object.TYPE_DIRECTORY
      elif (stat.S_ISCHR(stat_info.st_mode) or
            stat.S_ISBLK(stat_info.st_mode)):
        stat_object.type = stat_object.TYPE_DEVICE
      elif stat.S_ISFIFO(stat_info.st_mode):
        stat_object.type = stat_object.TYPE_PIPE
      elif stat.S_ISSOCK(stat_info.st_mode):
        stat_object.type = stat_object.TYPE_SOCKET

      # Other stat information.
      stat_object.ino = stat_info.st_ino
      # stat_info.st_dev
      # stat_info.st_nlink

    return stat_object

  @property
  def link(self):
    """The full path of the linked file entry."""
    if self._link is None:
      self._link = u''

      if not self.IsLink():
        return self._link

      location = getattr(self.path_spec, u'location', None)
      if location is None:
        return self._link

      self._link = os.readlink(location)
      self._link = os.path.abspath(self._link)
    return self._link

  @property
  def name(self):
    """The name of the file entry, which does not include the full path."""
    if self._name is None:
      location = getattr(self.path_spec, u'location', None)
      if location is not None:
        self._name = self._file_system.BasenamePath(location)
    return self._name

  @property
  def sub_file_entries(self):
    """The sub file entries (generator of instance of vfs.OSFileEntry)."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield OSFileEntry(self._resolver_context, self._file_system, path_spec)

  def GetLinkedFileEntry(self):
    """Retrieves the linked file entry, e.g. for a symbolic link."""
    link = self._GetLink()
    if not link:
      return

    path_spec = os_path_spec.OSPathSpec(location=link)
    return OSFileEntry(self._resolver_context, self._file_system, path_spec)

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      The parent file entry (instance of FileEntry) or None.
    """
    location = getattr(self.path_spec, u'location', None)
    if location is None:
      return

    parent_location = self._file_system.DirnamePath(location)
    if parent_location is None:
      return

    if parent_location == u'':
      parent_location = self._file_system.PATH_SEPARATOR

    path_spec = os_path_spec.OSPathSpec(location=parent_location)
    return OSFileEntry(self._resolver_context, self._file_system, path_spec)
