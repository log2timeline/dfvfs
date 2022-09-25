# -*- coding: utf-8 -*-
"""The FAT file entry implementation."""

import pyfsfat

from dfdatetime import definitions as dfdatetime_definitions
from dfdatetime import fat_date_time as dfdatetime_fat_date_time

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import fat_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import attribute
from dfvfs.vfs import extent
from dfvfs.vfs import fat_directory
from dfvfs.vfs import file_entry


class FATFileEntry(file_entry.FileEntry):
  """File system file entry that uses pyfsfat."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FAT

  _FILE_SYSTEM_FORMAT_EXFAT = pyfsfat.file_system_formats.EXFAT

  def __init__(
      self, resolver_context, file_system, path_spec, fsfat_file_entry=None,
      is_root=False, is_virtual=False):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      fsfat_file_entry (Optional[pyfsfat.file_entry]): FAT file entry.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
          entry emulated by the corresponding file system.

    Raises:
      BackEndError: if the pyfsfat file entry is missing.
    """
    if not fsfat_file_entry:
      fsfat_file_entry = file_system.GetFATFileEntryByPathSpec(path_spec)
    if not fsfat_file_entry:
      raise errors.BackEndError('Missing pyfsfat file entry.')

    fsfat_volume = file_system.GetFATVolume()

    if is_root:
      file_entry_name = ''
    else:
      file_entry_name = fsfat_file_entry.name

    super(FATFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._file_system_format = fsfat_volume.get_file_system_format()
    self._fsfat_file_entry = fsfat_file_entry
    self._name = file_entry_name

    file_attribute_flags = fsfat_file_entry.file_attribute_flags
    if (file_attribute_flags is None or
        file_attribute_flags & pyfsfat.file_attribute_flags.DIRECTORY):
      self.entry_type = definitions.FILE_ENTRY_TYPE_DIRECTORY
    elif file_attribute_flags & pyfsfat.file_attribute_flags.DEVICE:
      self.entry_type = definitions.FILE_ENTRY_TYPE_DEVICE
    else:
      self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      FATDirectory: directory or None if not available.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return None

    return fat_directory.FATDirectory(
        self._file_system, self.path_spec, self._fsfat_file_entry)

  def _GetStatAttribute(self):
    """Retrieves a stat attribute.

    Returns:
      StatAttribute: a stat attribute or None if not available.
    """
    stat_attribute = attribute.StatAttribute()
    stat_attribute.inode_number = self._fsfat_file_entry.identifier
    stat_attribute.size = self._fsfat_file_entry.size
    stat_attribute.type = self.entry_type

    return stat_attribute

  def _GetSubFileEntries(self):
    """Retrieves a sub file entries generator.

    Yields:
      FATFileEntry: a sub file entry.
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield FATFileEntry(self._resolver_context, self._file_system, path_spec)

  @property
  def access_time(self):
    """dfdatetime.DateTimeValues: access time or None if not available."""
    timestamp = self._fsfat_file_entry.get_access_time_as_integer()
    # Access time can be None if not present and 0 if not set.
    if not timestamp:
      return None

    if self._file_system_format == self._FILE_SYSTEM_FORMAT_EXFAT:
      precision = dfdatetime_definitions.PRECISION_10_MILLISECONDS
    else:
      precision = dfdatetime_definitions.PRECISION_1_DAY

    return dfdatetime_fat_date_time.FATTimestamp(
        precision=precision, timestamp=timestamp)

  @property
  def creation_time(self):
    """dfdatetime.DateTimeValues: creation time or None if not available."""
    timestamp = self._fsfat_file_entry.get_creation_time_as_integer()
    # Creation time can be None if not present and 0 if not set.
    if not timestamp:
      return None

    return dfdatetime_fat_date_time.FATTimestamp(
        precision=dfdatetime_definitions.PRECISION_10_MILLISECONDS,
        timestamp=timestamp)

  @property
  def name(self):
    """str: name of the file entry, which does not include the full path."""
    return self._name

  @property
  def modification_time(self):
    """dfdatetime.DateTimeValues: modification time or None if not available."""
    timestamp = self._fsfat_file_entry.get_modification_time_as_integer()
    # Modification time can be None if not present and 0 if not set.
    if not timestamp:
      return None

    if self._file_system_format == self._FILE_SYSTEM_FORMAT_EXFAT:
      precision = dfdatetime_definitions.PRECISION_10_MILLISECONDS
    else:
      precision = dfdatetime_definitions.PRECISION_2_SECONDS

    return dfdatetime_fat_date_time.FATTimestamp(
        precision=precision, timestamp=timestamp)

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    return self._fsfat_file_entry.size

  def GetExtents(self):
    """Retrieves the extents.

    Returns:
      list[Extent]: the extents.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_FILE:
      return []

    extents = []
    for extent_index in range(self._fsfat_file_entry.number_of_extents):
      extent_offset, extent_size, extent_flags = (
          self._fsfat_file_entry.get_extent(extent_index))

      if extent_flags & 0x1:
        extent_type = definitions.EXTENT_TYPE_SPARSE
      else:
        extent_type = definitions.EXTENT_TYPE_DATA

      data_stream_extent = extent.Extent(
          extent_type=extent_type, offset=extent_offset, size=extent_size)
      extents.append(data_stream_extent)

    return extents

  def GetFileObject(self, data_stream_name=''):
    """Retrieves a file-like object of a specific data stream.

    Args:
      data_stream_name (Optional[str]): name of the data stream, where an empty
          string represents the default data stream.

    Returns:
      FileIO: a file-like object or None if not available.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_FILE or data_stream_name:
      return None

    return resolver.Resolver.OpenFileObject(
        self.path_spec, resolver_context=self._resolver_context)

  def GetFATFileEntry(self):
    """Retrieves the FAT file entry.

    Returns:
      pyfsfat.file_entry: FAT file entry.
    """
    return self._fsfat_file_entry

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      FATFileEntry: parent file entry or None if not available.
    """
    parent_location = None

    location = getattr(self.path_spec, 'location', None)
    if location is not None:
      parent_location = self._file_system.DirnamePath(location)
      if parent_location == '':
        parent_location = self._file_system.PATH_SEPARATOR

    parent_path_spec = getattr(self.path_spec, 'parent', None)
    path_spec = fat_path_spec.FATPathSpec(
        location=parent_location, parent=parent_path_spec)

    is_root = bool(parent_location == self._file_system.LOCATION_ROOT)

    return FATFileEntry(
        self._resolver_context, self._file_system, path_spec, is_root=is_root)
