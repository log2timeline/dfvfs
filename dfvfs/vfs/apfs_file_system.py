# -*- coding: utf-8 -*-
"""The APFS file system implementation."""

from dfvfs.lib import apfs_helper
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import apfs_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system
from dfvfs.vfs import apfs_file_entry


class APFSFileSystem(file_system.FileSystem):
  """File system that uses pyfsapfs."""

  ROOT_DIRECTORY_IDENTIFIER = 2

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_APFS

  def __init__(self, resolver_context, path_spec):
    """Initializes an APFS file system.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(APFSFileSystem, self).__init__(resolver_context, path_spec)
    self._fsapfs_volume = None

  def _Close(self):
    """Closes the file system.

    Raises:
      IOError: if the close failed.
    """
    self._fsapfs_volume = None

  def _Open(self, mode='rb'):
    """Opens the file system defined by path specification.

    Args:
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the APFS volume could not be retrieved or unlocked.
      OSError: if the APFS volume could not be retrieved or unlocked.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not self._path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    if self._path_spec.parent.type_indicator != (
        definitions.TYPE_INDICATOR_APFS_CONTAINER):
      raise errors.PathSpecError(
          'Unsupported path specification not type APFS container.')

    apfs_container_file_system = resolver.Resolver.OpenFileSystem(
        self._path_spec.parent, resolver_context=self._resolver_context)

    fsapfs_volume = apfs_container_file_system.GetAPFSVolumeByPathSpec(
        self._path_spec.parent)
    if not fsapfs_volume:
      raise IOError('Unable to retrieve APFS volume')

    try:
      is_locked = not apfs_helper.APFSUnlockVolume(
          fsapfs_volume, self._path_spec.parent, resolver.Resolver.key_chain)
    except IOError as exception:
      raise IOError(f'Unable to unlock volume with error: {exception!s}')

    if is_locked:
      raise IOError('Unable to unlock volume.')

    self._fsapfs_volume = fsapfs_volume

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      bool: True if the file entry exists.

    Raises:
      BackEndError: if the file entry cannot be opened.
    """
    # Opening a file by location will ensure added time is provided when
    # available.
    fsapfs_file_entry = None
    location = getattr(path_spec, 'location', None)
    identifier = getattr(path_spec, 'identifier', None)

    try:
      if location is not None:
        fsapfs_file_entry = self._fsapfs_volume.get_file_entry_by_path(location)
      elif identifier is not None:
        fsapfs_file_entry = self._fsapfs_volume.get_file_entry_by_identifier(
            identifier)

    except IOError as exception:
      raise errors.BackEndError(exception)

    return fsapfs_file_entry is not None

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      APFSFileEntry: file entry or None if not available.

    Raises:
      BackEndError: if the file entry cannot be opened.
    """
    # Opening a file by location will ensure added time is provided when
    # available.
    fsapfs_file_entry = None
    location = getattr(path_spec, 'location', None)
    identifier = getattr(path_spec, 'identifier', None)

    if (location == self.LOCATION_ROOT or
        identifier == self.ROOT_DIRECTORY_IDENTIFIER):
      is_root = True
      # Note that APFS can have a volume without a root directory.
      fsapfs_file_entry = self._fsapfs_volume.get_root_directory()

    else:
      is_root = False
      try:
        if location is not None:
          fsapfs_file_entry = self._fsapfs_volume.get_file_entry_by_path(
              location)
        elif identifier is not None:
          fsapfs_file_entry = self._fsapfs_volume.get_file_entry_by_identifier(
              identifier)

      except IOError as exception:
        raise errors.BackEndError(exception)

    if fsapfs_file_entry is None:
      return None

    return apfs_file_entry.APFSFileEntry(
        self._resolver_context, self, path_spec,
        fsapfs_file_entry=fsapfs_file_entry, is_root=is_root)

  def GetAPFSFileEntryByPathSpec(self, path_spec):
    """Retrieves the APFS file entry for a path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      pyfsapfs.file_entry: file entry.

    Raises:
      PathSpecError: if the path specification is missing location and
          identifier.
    """
    # Opening a file by location will ensure added time is provided when
    # available.
    location = getattr(path_spec, 'location', None)
    identifier = getattr(path_spec, 'identifier', None)

    if location is not None:
      fsapfs_file_entry = self._fsapfs_volume.get_file_entry_by_path(location)
    elif identifier is not None:
      fsapfs_file_entry = self._fsapfs_volume.get_file_entry_by_identifier(
          identifier)
    else:
      raise errors.PathSpecError(
          'Path specification missing location and identifier.')

    return fsapfs_file_entry

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      APFSFileEntry: file entry or None if not available.
    """
    path_spec = apfs_path_spec.APFSPathSpec(
        location=self.LOCATION_ROOT, identifier=self.ROOT_DIRECTORY_IDENTIFIER,
        parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
