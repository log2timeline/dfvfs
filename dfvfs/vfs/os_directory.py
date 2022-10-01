# -*- coding: utf-8 -*-
"""The operating system directory implementation."""

import os

from dfvfs.lib import errors
from dfvfs.path import os_path_spec
from dfvfs.vfs import directory


class OSDirectory(directory.Directory):
  """File system directory that uses the operating system."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      OSPathSpec: a path specification.

    Raises:
      AccessError: if the access to list the directory was denied.
      BackEndError: if the directory could not be listed.
    """
    location = getattr(self.path_spec, 'location', None)
    if location is not None:
      # Windows will raise WindowsError, which can be caught by OSError,
      # if the process has no access to list the directory. The os.access()
      # function cannot be used since it will return true even when os.listdir()
      # fails.
      try:
        for directory_entry in os.listdir(location):
          directory_entry_location = self._file_system.JoinPath([
              location, directory_entry])
          yield os_path_spec.OSPathSpec(location=directory_entry_location)

      # Note that PermissionError needs to be defined before OSError.
      except PermissionError as exception:
        raise errors.AccessError((
            f'Access to directory: {location:s} denied with error: '
            f'{exception!s}'))

      except OSError as exception:
        raise errors.BackEndError((
            f'Unable to list directory: {location:s} with error: '
            f'{exception!s}'))
