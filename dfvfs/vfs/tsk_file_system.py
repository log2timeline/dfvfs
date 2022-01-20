# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) file system implementation."""

import pytsk3

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import tsk_image
from dfvfs.path import tsk_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system
from dfvfs.vfs import tsk_file_entry


class TSKFileSystem(file_system.FileSystem):
  """File system that uses pytsk3."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK

  def __init__(self, resolver_context, path_spec):
    """Initializes a file system.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(TSKFileSystem, self).__init__(resolver_context, path_spec)
    self._file_object = None
    self._tsk_file_system = None
    self._tsk_fs_type = None

  def _Close(self):
    """Closes a file system.

    Raises:
      IOError: if the close failed.
    """
    self._tsk_file_system = None
    self._file_object = None

  def _Open(self, mode='rb'):
    """Opens the file system object defined by path specification.

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

    tsk_image_object = tsk_image.TSKFileSystemImage(file_object)
    tsk_file_system = pytsk3.FS_Info(tsk_image_object)

    self._file_object = file_object
    self._tsk_file_system = tsk_file_system

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      bool: True if the file entry exists.
    """
    # Opening a file by inode number is faster than opening a file by location.
    tsk_file = None
    inode = getattr(path_spec, 'inode', None)
    location = getattr(path_spec, 'location', None)

    try:
      if inode is not None:
        tsk_file = self._tsk_file_system.open_meta(inode=inode)
      elif location is not None:
        tsk_file = self._tsk_file_system.open(location)

    except IOError:
      pass

    return tsk_file is not None

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      TSKFileEntry: a file entry or None if not available.
    """
    # Opening a file by inode number is faster than opening a file by location.
    tsk_file = None
    inode = getattr(path_spec, 'inode', None)
    location = getattr(path_spec, 'location', None)

    root_inode = self.GetRootInode()
    if (location == self.LOCATION_ROOT or
        (inode is not None and root_inode is not None and inode == root_inode)):
      tsk_file = self._tsk_file_system.open(self.LOCATION_ROOT)
      return tsk_file_entry.TSKFileEntry(
          self._resolver_context, self, path_spec, tsk_file=tsk_file,
          is_root=True)

    try:
      if inode is not None:
        tsk_file = self._tsk_file_system.open_meta(inode=inode)
      elif location is not None:
        tsk_file = self._tsk_file_system.open(location)

    except IOError:
      pass

    if tsk_file is None:
      return None

    # TODO: is there a way to determine the parent inode number here?
    return tsk_file_entry.TSKFileEntry(
        self._resolver_context, self, path_spec, tsk_file=tsk_file)

  def GetFsInfo(self):
    """Retrieves the file system info.

    Returns:
      pytsk3.FS_Info: file system info.
    """
    return self._tsk_file_system

  def GetFsType(self):
    """Retrieves the file system type.

    Returns:
      pytsk3.TSK_FS_TYPE_ENUM: file system type.
    """
    if self._tsk_fs_type is None:
      self._tsk_fs_type = pytsk3.TSK_FS_TYPE_UNSUPP
      if (not self._tsk_file_system or
          not hasattr(self._tsk_file_system, 'info')):
        return self._tsk_fs_type

      self._tsk_fs_type = getattr(
          self._tsk_file_system.info, 'ftype', pytsk3.TSK_FS_TYPE_UNSUPP)

    return self._tsk_fs_type

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      TSKFileEntry: a file entry.
    """
    kwargs = {}

    root_inode = self.GetRootInode()
    if root_inode is not None:
      kwargs['inode'] = root_inode

    kwargs['location'] = self.LOCATION_ROOT
    kwargs['parent'] = self._path_spec.parent

    path_spec = tsk_path_spec.TSKPathSpec(**kwargs)
    return self.GetFileEntryByPathSpec(path_spec)

  def GetRootInode(self):
    """Retrieves the root inode.

    Returns:
      int: inode number or None if not available.
    """
    # Note that because pytsk3.FS_Info does not explicitly define info
    # we need to check if the attribute exists and has a value other
    # than None
    if getattr(self._tsk_file_system, 'info', None) is None:
      return None

    # Note that because pytsk3.TSK_FS_INFO does not explicitly define
    # root_inum we need to check if the attribute exists and has a value
    # other than None
    return getattr(self._tsk_file_system.info, 'root_inum', None)

  def GetTSKFileByPathSpec(self, path_spec):
    """Retrieves the SleuthKit file object for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      pytsk3.File: TSK file.

    Raises:
      PathSpecError: if the path specification is missing inode and location.
    """
    # Opening a file by inode number is faster than opening a file
    # by location.
    inode = getattr(path_spec, 'inode', None)
    location = getattr(path_spec, 'location', None)

    if inode is not None:
      tsk_file = self._tsk_file_system.open_meta(inode=inode)
    elif location is not None:
      tsk_file = self._tsk_file_system.open(location)
    else:
      raise errors.PathSpecError(
          'Path specification missing inode and location.')

    return tsk_file

  def IsExt(self):
    """Determines if the file system is ext2, ext3 or ext4.

    Returns:
      bool: True if the file system is ext.
    """
    tsk_fs_type = self.GetFsType()
    return tsk_fs_type in [
        pytsk3.TSK_FS_TYPE_EXT2, pytsk3.TSK_FS_TYPE_EXT3,
        pytsk3.TSK_FS_TYPE_EXT4, pytsk3.TSK_FS_TYPE_EXT_DETECT]

  def IsHFS(self):
    """Determines if the file system is HFS, HFS+ or HFSX.

    Returns:
      bool: True if the file system is HFS.
    """
    tsk_fs_type = self.GetFsType()
    return tsk_fs_type in [
        pytsk3.TSK_FS_TYPE_HFS, pytsk3.TSK_FS_TYPE_HFS_DETECT]

  def IsNTFS(self):
    """Determines if the file system is NTFS.

    Returns:
      bool: True if the file system is NTFS.
    """
    tsk_fs_type = self.GetFsType()
    return tsk_fs_type in [
        pytsk3.TSK_FS_TYPE_NTFS, pytsk3.TSK_FS_TYPE_NTFS_DETECT]
