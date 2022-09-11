# -*- coding: utf-8 -*-
"""The FAT file system implementation."""

import pyfsfat

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import fat_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import fat_file_entry
from dfvfs.vfs import file_system


class FATFileSystem(file_system.FileSystem):
  """File system that uses pyfsfat."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FAT

  LOCATION_ROOT = '\\'
  PATH_SEPARATOR = '\\'

  def __init__(self, resolver_context, path_spec):
    """Initializes an FAT file system.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(FATFileSystem, self).__init__(resolver_context, path_spec)
    self._file_object = None
    self._fsfat_volume = None
    self._root_directory_identifier = None

  def _Close(self):
    """Closes the file system.

    Raises:
      IOError: if the close failed.
    """
    self._fsfat_volume = None
    self._file_object = None

  def _Open(self, mode='rb'):
    """Opens the file system defined by path specification.

    Args:
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not self._path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    file_object = resolver.Resolver.OpenFileObject(
        self._path_spec.parent, resolver_context=self._resolver_context)

    fsfat_volume = pyfsfat.volume()
    fsfat_volume.open_file_object(file_object)
    fsfat_root_directory = fsfat_volume.get_root_directory()

    self._file_object = file_object
    self._fsfat_volume = fsfat_volume
    self._root_directory_identifier = fsfat_root_directory.identifier

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      bool: True if the file entry exists.

    Raises:
      BackEndError: if the file entry cannot be opened.
    """
    # Opening a file by identifier is faster than opening a file by location.
    fsfat_file_entry = None
    location = getattr(path_spec, 'location', None)
    identifier = getattr(path_spec, 'identifier', None)

    try:
      if identifier is not None:
        fsfat_file_entry = self._fsfat_volume.get_file_entry_by_identifier(
            identifier)
      elif location is not None:
        fsfat_file_entry = self._fsfat_volume.get_file_entry_by_path(location)

    except IOError as exception:
      raise errors.BackEndError(exception)

    return fsfat_file_entry is not None

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      FATFileEntry: file entry or None if not available.

    Raises:
      BackEndError: if the file entry cannot be opened.
    """
    # Opening a file by identifier is faster than opening a file by location.
    fsfat_file_entry = None
    location = getattr(path_spec, 'location', None)
    identifier = getattr(path_spec, 'identifier', None)

    if (location == self.LOCATION_ROOT or
        identifier == self._root_directory_identifier):
      fsfat_file_entry = self._fsfat_volume.get_root_directory()
      return fat_file_entry.FATFileEntry(
          self._resolver_context, self, path_spec,
          fsfat_file_entry=fsfat_file_entry, is_root=True)

    try:
      if identifier is not None:
        fsfat_file_entry = self._fsfat_volume.get_file_entry_by_identifier(
            identifier)
      elif location is not None:
        fsfat_file_entry = self._fsfat_volume.get_file_entry_by_path(location)

    except IOError as exception:
      raise errors.BackEndError(exception)

    if fsfat_file_entry is None:
      return None

    return fat_file_entry.FATFileEntry(
        self._resolver_context, self, path_spec,
        fsfat_file_entry=fsfat_file_entry)

  def GetFATFileEntryByPathSpec(self, path_spec):
    """Retrieves the FAT file entry for a path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      pyfsfat.file_entry: file entry.

    Raises:
      PathSpecError: if the path specification is missing location and
          identifier.
    """
    # Opening a file by identifier is faster than opening a file by location.
    location = getattr(path_spec, 'location', None)
    identifier = getattr(path_spec, 'identifier', None)

    if identifier is not None:
      fsfat_file_entry = self._fsfat_volume.get_file_entry_by_identifier(
          identifier)
    elif location is not None:
      fsfat_file_entry = self._fsfat_volume.get_file_entry_by_path(location)
    else:
      raise errors.PathSpecError(
          'Path specification missing location and identifier.')

    return fsfat_file_entry

  def GetFATVolume(self):
    """Retrieves the FAT volume.

    Returns:
      pyfsfat.volume: a FAT volume.
    """
    return self._fsfat_volume

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      FATFileEntry: file entry.
    """
    path_spec = fat_path_spec.FATPathSpec(
        location=self.LOCATION_ROOT,
        identifier=self._root_directory_identifier,
        parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
