# -*- coding: utf-8 -*-
"""The Overlay file system implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import overlay_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system
from dfvfs.vfs import overlay_directory
from dfvfs.vfs import overlay_file_entry


class OverlayFileSystem(file_system.FileSystem):
  """Overlay file system."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_OVERLAY

  def __init__(self, resolver_context, path_spec,
               lower_path_spec=None, upper_path_spec=None):
    """Initializes a Overlay file system.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): the path specification.
      lower_path_spec (Optional[List[PathSpec]]): a list of path specifications
          for the lower layer(s) of the Overlay, ordered from top to bottom.
      upper_path_spec (Optional[PathSpec]): a path specification for the upper
          layer of the Overlay.

    Raises:
      BackEndError: if the lower and upper path specifications are not unique.
    """
    super(OverlayFileSystem, self).__init__(resolver_context, path_spec)

    # check that the lower and upper path specs are all unique
    combined_specs = lower_path_spec + [upper_path_spec]
    if len(set(combined_specs)) != len(combined_specs):
      raise errors.BackEndError(
          'Lower and/or uppor path specifications are not unique.')

    self.lower_path_specs = lower_path_spec
    self.upper_path_spec = upper_path_spec
    self._filesystem_layers = [
        None for _ in range(len(self.lower_path_specs) + 1)]

  def _Close(self):
    """Closes the Overlay file system."""
    self._filesystem_layers = [
        None for _ in range(len(self.lower_path_specs) + 1)]

  def _Open(self, mode='rb'):
    """Opens the file system defined by path specification.

    Args:
      mode (Optional[str]): file access mode. The default is 'rb' which
          represents read-only binary.

    Raises:
      BackEndError: if not able to open the lower/upper filesystem.
    """
    for i, layer_path_spec in enumerate(
        [self.upper_path_spec] + self.lower_path_specs):

      layer_file_system = resolver.Resolver.OpenFileSystem(
          layer_path_spec, self._resolver_context)
      if not layer_file_system:
        raise errors.BackEndError(
            'Unable to open the file system at layer {0:d}'.format(i))
      if not layer_file_system._is_open:  # pylint: disable=protected-access
        layer_file_system.Open()
      self._filesystem_layers[i] = layer_file_system

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      bool: True if the file entry exists.
    """
    try:
      file_entry = self.GetFileEntryByPathSpec(path_spec)
      return bool(file_entry)
    except errors.BackEndError:
      return False

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      OverlayFileEntry: file entry or None if not available.

    Raises:
      BackEndError: if the file entry cannot be opened.
    """
    location = getattr(path_spec, 'location', None)
    if location == self.LOCATION_ROOT:
      return overlay_file_entry.OverlayFileEntry(
          self._resolver_context, self, path_spec, is_root=True)
    path_elements = location.split(self.PATH_SEPARATOR)
    base_path = self.PATH_SEPARATOR + self.PATH_SEPARATOR.join(
        path_elements[1:-1])
    search_spec = overlay_path_spec.OverlayPathSpec(location=base_path)

    overlay_dir = overlay_directory.OverlayDirectory(self, search_spec)
    for entry in overlay_dir.entries:
      if entry.location == location:
        return overlay_file_entry.OverlayFileEntry(
            self._resolver_context, self, entry, is_root=False)

    return None

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      OverlayFileEntry: a file entry or None if not available.
    """
    path_spec = overlay_path_spec.OverlayPathSpec(
        location=self.LOCATION_ROOT)
    return self.GetFileEntryByPathSpec(path_spec)
