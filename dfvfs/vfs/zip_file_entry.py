# -*- coding: utf-8 -*-
"""The zip file entry implementation."""

from dfdatetime import time_elements as dfdatetime_time_elements

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import py2to3
from dfvfs.path import zip_path_spec
from dfvfs.vfs import file_entry
from dfvfs.vfs import vfs_stat


class ZipDirectory(file_entry.Directory):
  """Class that implements a directory object using zipfile."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      A path specification (instance of path.ZipPathSpec).
    """
    location = getattr(self.path_spec, u'location', None)

    if (location is None or
        not location.startswith(self._file_system.PATH_SEPARATOR)):
      return

    zip_file = self._file_system.GetZipFile()
    for zip_info in zip_file.infolist():
      path = getattr(zip_info, u'filename', None)
      if path is not None and not isinstance(path, py2to3.UNICODE_TYPE):
        try:
          path = path.decode(self._file_system.encoding)
        except UnicodeDecodeError:
          path = None

      if not path or not path.startswith(location[1:]):
        continue

      _, suffix = self._file_system.GetPathSegmentAndSuffix(location[1:], path)

      # Ignore anything that is part of a sub directory or the directory itself.
      if suffix or path == location[1:]:
        continue

      path_spec_location = self._file_system.JoinPath([path])

      # Restore / at end path to indicate a directory.
      if path.endswith(self._file_system.PATH_SEPARATOR):
        path_spec_location += self._file_system.PATH_SEPARATOR

      yield zip_path_spec.ZipPathSpec(
          location=path_spec_location, parent=self.path_spec.parent)


class ZipFileEntry(file_entry.FileEntry):
  """Class that implements a file entry object using zipfile."""

  _CREATOR_SYSTEM_MSDOS_COMPATIBLE = 0
  _CREATOR_SYSTEM_UNIX = 3
  _CREATOR_SYSTEM_WINDOWS_NT = 10
  _CREATOR_SYSTEM_VFAT = 14
  _CREATOR_SYSTEM_MACOSX = 19

  _MSDOS_FILE_ATTRIBUTES_IS_DIRECTORY = 0x10

  _UNIX_FILE_ATTRIBUTES_IS_DIRECTORY = 0x8000

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ZIP

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False, zip_info=None):
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
      zip_info: optional zip info object (instance of zipfile.ZipInfo).
    """
    super(ZipFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._zip_info = zip_info

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      A directory object (instance of Directory) or None.
    """
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if (self._stat_object and
        self._stat_object.type == self._stat_object.TYPE_DIRECTORY):
      return ZipDirectory(self._file_system, self.path_spec)
    return

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of vfs.VFSStat).

    Raises:
      BackEndError: when the zip info is missing in a non-virtual file entry.
    """
    zip_info = self.GetZipInfo()
    if not self._is_virtual and zip_info is None:
      raise errors.BackEndError(u'Missing zip info in non-virtual file entry.')

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    if zip_info is not None:
      stat_object.size = getattr(zip_info, u'file_size', None)

    # Date and time stat information.
    # TODO: move this to a timelib equivalent.
    zip_info_date_time = getattr(zip_info, u'date_time', None)
    if zip_info_date_time:
      date_time_values = dfdatetime_time_elements.TimeElements(
          zip_info_date_time)

      stat_time, stat_time_nano = date_time_values.CopyToStatTimeTuple()
      if stat_time is not None:
        stat_object.mtime = stat_time
        stat_object.mtime_nano = stat_time_nano

    # Ownership and permissions stat information.
    if zip_info is not None:
      creator_system = getattr(zip_info, u'create_system', 0)
      external_attributes = getattr(zip_info, u'external_attr', 0)

      if external_attributes != 0:
        if creator_system == self._CREATOR_SYSTEM_UNIX:
          st_mode = external_attributes >> 16
          stat_object.mode = st_mode & 0x0fff

    # File entry type stat information.

    # The root file entry is virtual and should have type directory.
    if (self._is_virtual or
        external_attributes & self._MSDOS_FILE_ATTRIBUTES_IS_DIRECTORY):
      stat_object.type = stat_object.TYPE_DIRECTORY
    else:
      stat_object.type = stat_object.TYPE_FILE

    # Other stat information.
    # zip_info.compress_type
    # zip_info.comment
    # zip_info.extra
    # zip_info.create_version
    # zip_info.extract_version
    # zip_info.flag_bits
    # zip_info.volume
    # zip_info.internal_attr
    # zip_info.compress_size

    return stat_object

  @property
  def name(self):
    """The name of the file entry, which does not include the full path."""
    zip_info = self.GetZipInfo()

    # Note that the root file entry is virtual and has no zip_info.
    if zip_info is None:
      return u''

    return self._file_system.BasenamePath(zip_info.filename)

  @property
  def sub_file_entries(self):
    """The sub file entries (generator of instance of vfs.FileEntry)."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield ZipFileEntry(self._resolver_context, self._file_system, path_spec)

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

    parent_path_spec = getattr(self.path_spec, u'parent', None)
    path_spec = zip_path_spec.ZipPathSpec(
        location=parent_location, parent=parent_path_spec)
    return ZipFileEntry(self._resolver_context, self._file_system, path_spec)

  def GetZipInfo(self):
    """Retrieves the zip info object.

    Returns:
      The zip info object (instance of zipfile.ZipInfo).

    Raises:
      ValueError: if the path specification is incorrect.
    """
    if not self._zip_info:
      location = getattr(self.path_spec, u'location', None)
      if location is None:
        raise ValueError(u'Path specification missing location.')

      if not location.startswith(self._file_system.LOCATION_ROOT):
        raise ValueError(u'Invalid location in path specification.')

      if len(location) == 1:
        return

      zip_file = self._file_system.GetZipFile()
      self._zip_info = zip_file.getinfo(location[1:])
    return self._zip_info
