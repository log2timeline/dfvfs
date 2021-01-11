# -*- coding: utf-8 -*-
"""The XFS file system implementation."""

import pyfsxfs

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import xfs_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system
from dfvfs.vfs import xfs_file_entry


class XFSFileSystem(file_system.FileSystem):
  """File system that uses pyfsxfs."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_XFS

  def __init__(self, resolver_context, path_spec):
    """Initializes an XFS file system.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(XFSFileSystem, self).__init__(resolver_context, path_spec)
    self._file_object = None
    self._fsxfs_volume = None
    self._root_directory_inode_number = None

  def _Close(self):
    """Closes the file system.

    Raises:
      IOError: if the close failed.
    """
    self._fsxfs_volume = None
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

    fsxfs_volume = pyfsxfs.volume()
    fsxfs_volume.open_file_object(file_object)

    fsxfs_root_directory = fsxfs_volume.get_root_directory()

    self._file_object = file_object
    self._fsxfs_volume = fsxfs_volume
    self._root_directory_inode_number = fsxfs_root_directory.get_inode_number()

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      bool: True if the file entry exists.

    Raises:
      BackEndError: if the file entry cannot be opened.
    """
    # Opening a file by inode is faster than opening a file by location.
    fsxfs_file_entry = None
    location = getattr(path_spec, 'location', None)
    inode = getattr(path_spec, 'inode', None)

    try:
      if inode is not None:
        fsxfs_file_entry = self._fsxfs_volume.get_file_entry_by_inode(inode)
      elif location is not None:
        fsxfs_file_entry = self._fsxfs_volume.get_file_entry_by_path(location)

    except IOError as exception:
      raise errors.BackEndError(exception)

    return fsxfs_file_entry is not None

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      XFSFileEntry: file entry or None if not available.

    Raises:
      BackEndError: if the file entry cannot be opened.
    """
    # Opening a file by inode is faster than opening a file by location.
    fsxfs_file_entry = None
    location = getattr(path_spec, 'location', None)
    inode = getattr(path_spec, 'inode', None)

    if (location == self.LOCATION_ROOT or
        inode == self._root_directory_inode_number):
      fsxfs_file_entry = self._fsxfs_volume.get_root_directory()
      return xfs_file_entry.XFSFileEntry(
          self._resolver_context, self, path_spec,
          fsxfs_file_entry=fsxfs_file_entry, is_root=True)

    try:
      if inode is not None:
        fsxfs_file_entry = self._fsxfs_volume.get_file_entry_by_inode(
            inode)
      elif location is not None:
        fsxfs_file_entry = self._fsxfs_volume.get_file_entry_by_path(location)

    except IOError as exception:
      raise errors.BackEndError(exception)

    if fsxfs_file_entry is None:
      return None

    return xfs_file_entry.XFSFileEntry(
        self._resolver_context, self, path_spec,
        fsxfs_file_entry=fsxfs_file_entry)

  def GetXFSFileEntryByPathSpec(self, path_spec):
    """Retrieves the XFS file entry for a path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      pyfsxfs.file_entry: file entry.

    Raises:
      PathSpecError: if the path specification is missing location and
          inode.
    """
    # Opening a file by inode is faster than opening a file by location.
    location = getattr(path_spec, 'location', None)
    inode = getattr(path_spec, 'inode', None)

    if inode is not None:
      fsxfs_file_entry = self._fsxfs_volume.get_file_entry_by_inode(inode)
    elif location is not None:
      fsxfs_file_entry = self._fsxfs_volume.get_file_entry_by_path(location)
    else:
      raise errors.PathSpecError(
          'Path specification missing location and inode.')

    return fsxfs_file_entry

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      XFSFileEntry: file entry.
    """
    path_spec = xfs_path_spec.XFSPathSpec(
        location=self.LOCATION_ROOT, inode=self._root_directory_inode_number,
        parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
