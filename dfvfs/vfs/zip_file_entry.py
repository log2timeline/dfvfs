# -*- coding: utf-8 -*-
"""The ZIP file entry implementation."""

from dfdatetime import time_elements as dfdatetime_time_elements

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import zip_path_spec
from dfvfs.vfs import attribute
from dfvfs.vfs import file_entry
from dfvfs.vfs import zip_directory


class ZipFileEntry(file_entry.FileEntry):
  """File system file entry that uses zipfile."""

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
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
          entry emulated by the corresponding file system.
      zip_info (Optional[zipfile.ZipInfo]): ZIP information.

    Raises:
      BackEndError: when the zip info is missing in a non-virtual file entry.
    """
    if not is_virtual and zip_info is None:
      zip_info = file_system.GetZipInfoByPathSpec(path_spec)
    if not is_virtual and zip_info is None:
      raise errors.BackEndError('Missing zip info in non-virtual file entry.')

    super(ZipFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._creator_system = getattr(zip_info, 'create_system', 0)
    self._external_attributes = getattr(zip_info, 'external_attr', 0)
    self._zip_info = zip_info

    if (is_virtual or
        self._external_attributes & self._MSDOS_FILE_ATTRIBUTES_IS_DIRECTORY):
      self.entry_type = definitions.FILE_ENTRY_TYPE_DIRECTORY
    else:
      self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      ZIPDirectory: a directory.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return None

    return zip_directory.ZIPDirectory(self._file_system, self.path_spec)

  def _GetStatAttribute(self):
    """Retrieves a stat attribute.

    Returns:
      StatAttribute: a stat attribute or None if not available.
    """
    stat_attribute = attribute.StatAttribute()
    stat_attribute.size = getattr(self._zip_info, 'file_size', None)
    stat_attribute.type = self.entry_type

    if self._zip_info is not None:
      # Ownership and permissions stat information.
      if self._external_attributes != 0:
        if self._creator_system == self._CREATOR_SYSTEM_UNIX:
          stat_attribute.mode = self._external_attributes >> 16

    return stat_attribute

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      ZipFileEntry: a sub file entry.
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      zip_file = self._file_system.GetZipFile()
      if zip_file:
        for path_spec in self._directory.entries:
          location = getattr(path_spec, 'location', None)
          if location is None:
            continue

          kwargs = {}
          try:
            kwargs['zip_info'] = zip_file.getinfo(location[1:])
          except KeyError:
            kwargs['is_virtual'] = True

          yield ZipFileEntry(
              self._resolver_context, self._file_system, path_spec, **kwargs)

  @property
  def modification_time(self):
    """dfdatetime.DateTimeValues: modification time or None if not available."""
    if self._zip_info is None:
      return None

    time_elements = getattr(self._zip_info, 'date_time', None)
    return dfdatetime_time_elements.TimeElements(
        time_elements_tuple=time_elements)

  @property
  def name(self):
    """str: name of the file entry, without the full path."""
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
    return getattr(self._zip_info, 'file_size', None)

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      ZipFileEntry: parent file entry or None if not available.
    """
    location = getattr(self.path_spec, 'location', None)
    if location is None:
      return None

    parent_location = self._file_system.DirnamePath(location)
    if parent_location is None:
      return None

    parent_path_spec = getattr(self.path_spec, 'parent', None)

    if parent_location == '':
      parent_location = self._file_system.PATH_SEPARATOR
      is_root = True
      is_virtual = True
    else:
      is_root = False
      is_virtual = False

    path_spec = zip_path_spec.ZipPathSpec(
        location=parent_location, parent=parent_path_spec)
    return ZipFileEntry(
        self._resolver_context, self._file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)

  def GetZipInfo(self):
    """Retrieves the ZIP info object.

    Returns:
      zipfile.ZipInfo: a ZIP info object or None if not available.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """
    if not self._zip_info:
      location = getattr(self.path_spec, 'location', None)
      if location is None:
        raise errors.PathSpecError('Path specification missing location.')

      if not location.startswith(self._file_system.LOCATION_ROOT):
        raise errors.PathSpecError('Invalid location in path specification.')

      if len(location) == 1:
        return None

      zip_file = self._file_system.GetZipFile()
      try:
        self._zip_info = zip_file.getinfo(location[1:])
      except KeyError:
        pass

    return self._zip_info
