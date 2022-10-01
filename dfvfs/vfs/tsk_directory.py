# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) directory implementation."""

import pytsk3

from dfvfs.lib import errors
from dfvfs.path import tsk_path_spec
from dfvfs.vfs import directory


class TSKDirectory(directory.Directory):
  """File system directory that uses pytsk3."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      TSKPathSpec: a path specification.

    Raises:
      BackEndError: if pytsk3 cannot open the directory.
    """
    # Opening a file by inode number is faster than opening a file
    # by location.
    inode = getattr(self.path_spec, 'inode', None)
    location = getattr(self.path_spec, 'location', None)

    fs_info = self._file_system.GetFsInfo()
    tsk_directory = None

    try:
      if inode is not None:
        tsk_directory = fs_info.open_dir(inode=inode)
      elif location is not None:
        tsk_directory = fs_info.open_dir(path=location)

    except IOError as exception:
      raise errors.BackEndError(
          f'Unable to open directory with error: {exception!s}')

    if tsk_directory:
      for tsk_directory_entry in tsk_directory:
        # Note that because pytsk3.Directory does not explicitly define info
        # we need to check if the attribute exists and has a value other
        # than None.
        if getattr(tsk_directory_entry, 'info', None) is None:
          continue

        # Note that because pytsk3.TSK_FS_FILE does not explicitly define
        # fs_info we need to check if the attribute exists and has a value
        # other than None.
        if getattr(tsk_directory_entry.info, 'fs_info', None) is None:
          continue

        # Note that because pytsk3.TSK_FS_FILE does not explicitly define meta
        # we need to check if the attribute exists and has a value other
        # than None.
        if getattr(tsk_directory_entry.info, 'meta', None) is None:
          # Most directory entries will have an "inode" but not all, e.g.
          # previously deleted files. Currently directory entries without
          # a pytsk3.TSK_FS_META object are ignored.
          continue

        # Note that because pytsk3.TSK_FS_META does not explicitly define addr
        # we need to check if the attribute exists.
        if not hasattr(tsk_directory_entry.info.meta, 'addr'):
          continue

        directory_entry_inode = tsk_directory_entry.info.meta.addr
        directory_entry = None

        # Ignore references to self.
        if directory_entry_inode == inode:
          continue

        # On non-NTFS file systems ignore inode 0.
        if directory_entry_inode == 0 and not self._file_system.IsNTFS():
          continue

        # Note that because pytsk3.TSK_FS_FILE does not explicitly define name
        # we need to check if the attribute exists and has a value other
        # than None.
        if getattr(tsk_directory_entry.info, 'name', None) is not None:
          # Ignore file entries marked as "unallocated".
          flags = getattr(tsk_directory_entry.info.name, 'flags', 0)
          if int(flags) & pytsk3.TSK_FS_NAME_FLAG_UNALLOC:
            continue

          directory_entry = getattr(tsk_directory_entry.info.name, 'name', '')

          try:
            # pytsk3 returns an UTF-8 encoded byte string.
            directory_entry = directory_entry.decode('utf8')
          except UnicodeError:
            # Continue here since we cannot represent the directory entry.
            continue

          if directory_entry:
            # Ignore references to self or parent.
            if directory_entry in ['.', '..']:
              continue

            if not location or location == self._file_system.PATH_SEPARATOR:
              directory_entry = self._file_system.JoinPath([directory_entry])
            else:
              directory_entry = self._file_system.JoinPath([
                  location, directory_entry])

        yield tsk_path_spec.TSKPathSpec(
            inode=directory_entry_inode, location=directory_entry,
            parent=self.path_spec.parent)
