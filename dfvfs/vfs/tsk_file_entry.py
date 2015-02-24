# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) file entry implementation."""

import pytsk3

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import tsk_path_spec
from dfvfs.vfs import file_entry
from dfvfs.vfs import vfs_stat


class TSKDirectory(file_entry.Directory):
  """Class that implements a directory object using pytsk3."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

       Since a directory can contain a vast number of entries using
       a generator is more memory efficient.

    Yields:
      A path specification (instance of path.TSKPathSpec).
    """
    # Opening a file by inode number is faster than opening a file
    # by location.
    inode = getattr(self.path_spec, u'inode', None)
    location = getattr(self.path_spec, u'location', None)

    fs_info = self._file_system.GetFsInfo()
    if inode is not None:
      tsk_directory = fs_info.open_dir(inode=inode)
    elif location is not None:
      tsk_directory = fs_info.open_dir(path=location)
    else:
      return

    for tsk_directory_entry in tsk_directory:
      # Note that because pytsk3.Directory does not explicitly defines info
      # we need to check if the attribute exists and has a value other
      # than None.
      if getattr(tsk_directory_entry, u'info', None) is None:
        continue

      # Note that because pytsk3.TSK_FS_FILE does not explicitly defines fs_info
      # we need to check if the attribute exists and has a value other
      # than None.
      if getattr(tsk_directory_entry.info, u'fs_info', None) is None:
        continue

      # Note that because pytsk3.TSK_FS_FILE does not explicitly defines meta
      # we need to check if the attribute exists and has a value other
      # than None.
      if getattr(tsk_directory_entry.info, u'meta', None) is None:
        # Most directory entries will have an "inode" but not all, e.g.
        # previously deleted files. Currently directory entries without
        # a pytsk3.TSK_FS_META object are ignored.
        continue

      # Note that because pytsk3.TSK_FS_META does not explicitly defines addr
      # we need to check if the attribute exists.
      if not hasattr(tsk_directory_entry.info.meta, u'addr'):
        continue

      directory_entry_inode = tsk_directory_entry.info.meta.addr
      directory_entry = None

      # Ignore references to self.
      if directory_entry_inode == inode:
        continue

      # TODO: need better file system support.
      # On non-NTFS file systems ignore inode 0.
      ftype = tsk_directory_entry.info.fs_info.ftype
      if directory_entry_inode == 0 and ftype not in [
          pytsk3.TSK_FS_TYPE_NTFS, pytsk3.TSK_FS_TYPE_NTFS_DETECT]:
        continue

      # Note that because pytsk3.TSK_FS_FILE does not explicitly defines name
      # we need to check if the attribute exists and has a value other
      # than None.
      if getattr(tsk_directory_entry.info, u'name', None) is not None:
        directory_entry = getattr(tsk_directory_entry.info.name, u'name', u'')

        # pytsk3 returns a UTF-8 encoded byte string.
        try:
          directory_entry = directory_entry.decode(u'utf8')
        except UnicodeError:
          # Continue here since we cannot represent the directory entry.
          continue

        if directory_entry:
          # Ignore references to self or parent.
          if directory_entry in [u'.', u'..']:
            continue

          if location == self._file_system.PATH_SEPARATOR:
            directory_entry = self._file_system.JoinPath([directory_entry])
          else:
            directory_entry = self._file_system.JoinPath([
                location, directory_entry])

      yield tsk_path_spec.TSKPathSpec(
          inode=directory_entry_inode, location=directory_entry,
          parent=self.path_spec.parent)


class TSKFileEntry(file_entry.FileEntry):
  """Class that implements a file entry object using pytsk3."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False, tsk_file=None, parent_inode=None):
    """Initializes the file entry object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification (instance of path.PathSpec).
      is_root: optional boolean value to indicate if the file entry is
               the root file entry of the corresponding file system.
               The default is False.
      is_virtual: optional boolean value to indicate if the file entry is
                  a virtual file entry emulated by the corresponding file
                  system. The default is False.
      tsk_file: optional file object (instance of pytsk3.File).
                The default is None.
      parent_inode: optional parent inode number. The default is None.
    """
    super(TSKFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._link = None
    self._name = None
    self._parent_inode = parent_inode
    self._tsk_file = tsk_file

  def _GetDirectory(self):
    """Retrieves the directory object (instance of TSKDirectory)."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if (self._stat_object and
        self._stat_object.type == self._stat_object.TYPE_DIRECTORY):
      return TSKDirectory(self._file_system, self.path_spec)
    return

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of vfs.VFSStat).

    Raises:
      BackEndError: when the tsk File .info or .info.meta attribute is missing.
    """
    tsk_file = self.GetTSKFile()
    if not tsk_file or not tsk_file.info or not tsk_file.info.meta:
      raise errors.BackEndError(u'Missing tsk File .info or .info.meta.')

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    stat_object.size = getattr(tsk_file.info.meta, u'size', None)

    # Date and time stat information.
    stat_object.atime = getattr(tsk_file.info.meta, u'atime', None)
    stat_object.atime_nano = getattr(
        tsk_file.info.meta, u'atime_nano', None)
    stat_object.bkup_time = getattr(
        tsk_file.info.meta, u'bkup_time', None)
    stat_object.bkup_time_nano = getattr(
        tsk_file.info.meta, u'bkup_time_nano', None)
    stat_object.ctime = getattr(tsk_file.info.meta, u'ctime', None)
    stat_object.ctime_nano = getattr(
        tsk_file.info.meta, u'ctime_nano', None)
    stat_object.crtime = getattr(tsk_file.info.meta, u'crtime', None)
    stat_object.crtime_nano = getattr(
        tsk_file.info.meta, u'crtime_nano', None)
    stat_object.dtime = getattr(tsk_file.info.meta, u'dtime', None)
    stat_object.dtime_nano = getattr(
        tsk_file.info.meta, u'dtime_nano', None)
    stat_object.mtime = getattr(tsk_file.info.meta, u'mtime', None)
    stat_object.mtime_nano = getattr(
        tsk_file.info.meta, u'mtime_nano', None)

    # Ownership and permissions stat information.
    stat_object.mode = getattr(tsk_file.info.meta, u'mode', None)
    stat_object.uid = getattr(tsk_file.info.meta, u'uid', None)
    stat_object.gid = getattr(tsk_file.info.meta, u'gid', None)

    # File entry type stat information.
    # The type is an instance of pytsk3.TSK_FS_META_TYPE_ENUM.
    tsk_fs_meta_type = getattr(
        tsk_file.info.meta, u'type', pytsk3.TSK_FS_META_TYPE_UNDEF)

    if tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_REG:
      stat_object.type = stat_object.TYPE_FILE
    elif tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_DIR:
      stat_object.type = stat_object.TYPE_DIRECTORY
    elif tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_LNK:
      stat_object.type = stat_object.TYPE_LINK
    elif (tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_CHR or
          tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_BLK):
      stat_object.type = stat_object.TYPE_DEVICE
    elif tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_FIFO:
      stat_object.type = stat_object.TYPE_PIPE
    elif tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_SOCK:
      stat_object.type = stat_object.TYPE_SOCKET
    # TODO: implement support for:
    # pytsk3.TSK_FS_META_TYPE_UNDEF
    # pytsk3.TSK_FS_META_TYPE_SHAD
    # pytsk3.TSK_FS_META_TYPE_WHT
    # pytsk3.TSK_FS_META_TYPE_VIRT

    # Other stat information.
    stat_object.ino = getattr(tsk_file.info.meta, u'addr', None)
    # stat_object.dev = stat_info.st_dev
    # stat_object.nlink = getattr(tsk_file.info.meta, u'nlink', None)
    # stat_object.fs_type = u'Unknown'

    flags = getattr(tsk_file.info.meta, u'flags', 0)

    # The flags are an instance of pytsk3.TSK_FS_META_FLAG_ENUM.
    if int(flags) & pytsk3.TSK_FS_META_FLAG_ALLOC:
      stat_object.is_allocated = True
    else:
      stat_object.is_allocated = False

    return stat_object

  @property
  def link(self):
    """The full path of the linked file entry."""
    if self._link is None:
      self._link = u''

      if not self.IsLink():
        return self._link

      tsk_file = self.GetTSKFile()

      # Note that because pytsk3.File does not explicitly defines info
      # we need to check if the attribute exists and has a value other
      # than None.
      if getattr(tsk_file, u'info', None) is None:
        return self._link

      # If pytsk3.FS_Info.open() was used file.info has an attribute meta
      # (pytsk3.TSK_FS_META) that contains the link.
      if getattr(tsk_file.info, u'meta', None) is None:
        return self._link

      link = getattr(tsk_file.info.meta, u'link', None)

      if link is None:
        return self._link

      # pytsk3 returns a UTF-8 encoded byte string without a leading
      # path segment separator.
      try:
        link = u'{0:s}{1:s}'.format(
          self._file_system.PATH_SEPARATOR, link.decode(u'utf8'))
      except UnicodeError:
        raise errors.BackEndError(
            u'pytsk3 returned a non UTF-8 formatted link.')

      self._link = link
    return self._link

  @property
  def name(self):
    """The name of the file entry, which does not include the full path.

    Raises:
      BackEndError: when the pytsk3 returns a non UTF-8 formatted name.
    """
    if self._name is None:
      tsk_file = self.GetTSKFile()

      # Note that because pytsk3.File does not explicitly defines info
      # we need to check if the attribute exists and has a value other
      # than None.
      if getattr(tsk_file, u'info', None) is None:
        return

      # If pytsk3.FS_Info.open() was used file.info has an attribute name
      # (pytsk3.TSK_FS_FILE) that contains the name string. Otherwise the
      # name from the path specification is used.
      if getattr(tsk_file.info, u'name', None) is not None:
        name = getattr(tsk_file.info.name, u'name', None)

        # pytsk3 returns a UTF-8 encoded byte string.
        try:
          self._name = name.decode(u'utf8')
        except UnicodeError:
          raise errors.BackEndError(
              u'pytsk3 returned a non UTF-8 formatted name.')

      else:
        location = getattr(self.path_spec, u'location', None)
        if location:
          self._name = self._file_system.BasenamePath(location)

    return self._name

  @property
  def sub_file_entries(self):
    """The sub file entries (generator of instance of vfs.FileEntry)."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield TSKFileEntry(self._resolver_context, self._file_system, path_spec)

  def GetLinkedFileEntry(self):
    """Retrieves the linked file entry, e.g. for a symbolic link."""
    if not self.link:
      return

    parent_path_spec = getattr(self.path_spec, u'parent', None)
    path_spec = tsk_path_spec.TSKPathSpec(
        location=self.link, parent=parent_path_spec)
    # TODO: is there a way to determine the inode number here?
    return TSKFileEntry(self._resolver_context, self._file_system, path_spec)

  def GetParentFileEntry(self):
    """Retrieves the parent file entry."""
    location = getattr(self.path_spec, u'location', None)
    if location is None:
      return
    parent_inode = self._parent_inode
    parent_location = self._file_system.DirnamePath(location)
    if parent_inode is None and parent_location is None:
      return
    if parent_location == u'':
      parent_location = self._file_system.PATH_SEPARATOR

    parent_path_spec = getattr(self.path_spec, u'parent', None)
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=parent_inode, location=parent_location, parent=parent_path_spec)
    return TSKFileEntry(self._resolver_context, self._file_system, path_spec)

  def GetTSKFile(self):
    """Retrieves the SleuthKit file object (instance of pytsk3.File)."""
    if not self._tsk_file:
      fs_info = self._file_system.GetFsInfo()

      # Opening a file by inode number is faster than opening a file
      # by location.
      inode = getattr(self.path_spec, u'inode', None)
      location = getattr(self.path_spec, u'location', None)

      if inode is not None:
        self._tsk_file = fs_info.open_meta(inode=inode)
      elif location is not None:
        self._tsk_file = fs_info.open(location)
      else:
        raise RuntimeError(u'Path specification missing inode and location.')

    return self._tsk_file
