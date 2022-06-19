# -*- coding: utf-8 -*-
"""The Overlay directory implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory
from dfvfs.resolver import resolver
from dfvfs.vfs import directory


class OverlayDirectory(directory.Directory):
  """Overlay directory."""

  # pylint: disable=useless-super-delegation
  def __init__(self, file_system, path_spec):
    """Initializes an Overlay directory.

    Args:
      file_system (OverlayFileSystem): file system.
      path_spec (OverlayPathSpec): path specification.
    """
    super(OverlayDirectory, self).__init__(file_system, path_spec)

  def _ReadDirectory(self, location):
    """Enumerates the upper and lower layers of the Overlay filesystem.

    Args:
      location (str): the location in the Overlay.

    Yields:
      OverlayPathSpec: Overlay Path Specification.
    """
    visited_paths = set([location])
    whiteouts = set()

    resolver_context = self._file_system._resolver_context  # pylint: disable=protected-access

    layer_specs = [self._file_system.upper_path_spec]
    layer_specs.extend(self._file_system.lower_path_specs)

    for index, layer in enumerate(layer_specs):
      if location in whiteouts:
        continue

      layer_filesystem = self._file_system._filesystem_layers[index]  # pylint: disable=protected-access
      layer_path_spec = factory.Factory.NewPathSpec(
          layer.type_indicator, location=layer.location + location,
          parent=layer.parent)

      if not layer_path_spec:
        continue

      if not layer_filesystem.FileEntryExistsByPathSpec(layer_path_spec):
        continue
      layer_file_entry = resolver.Resolver.OpenFileEntry(
          layer_path_spec, resolver_context=resolver_context)

      for attribute in layer_file_entry.attributes:
        if (attribute.name == 'trusted.overlay.opaque' and
            attribute.read() == b'y'):
          whiteouts.add(location)

      if not layer_file_entry.IsDirectory():
        continue

      layer_directory = layer_file_entry._GetDirectory()  # pylint: disable=protected-access

      for subentry_spec in layer_directory.entries:
        overlay_path = subentry_spec.location[len(layer.location):]
        if overlay_path in visited_paths:
          continue

        if overlay_path in whiteouts:
          continue

        subentry = resolver.Resolver.OpenFileEntry(subentry_spec)
        stat = subentry.GetStatAttribute()

        if stat.type == definitions.FILE_ENTRY_TYPE_CHARACTER: # and device == 0/0:  # pylint: disable=line-too-long
          whiteouts.add(overlay_path)
          continue

        if stat.type == definitions.FILE_ENTRY_TYPE_DIRECTORY:
          for attribute in subentry.attributes:
            if (attribute.name == 'trusted.overlay.opaque' and
                attribute.read() == b'y'):
              whiteouts.add(overlay_path)
              break

        if overlay_path in visited_paths:
          continue
        visited_paths.add(overlay_path)

        overlay_path_spec = factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OVERLAY, location=overlay_path,
            parent=subentry_spec)
        yield overlay_path_spec

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      OverlayPathSpec: Overlay path specification.
    """
    try:
      fsoverlay_file_entry = self._file_system.GetFileEntryByPathSpec(
          self.path_spec)
    except errors.PathSpecError:
      return

    if not fsoverlay_file_entry:
      return

    location = getattr(self.path_spec, 'location', None)
    yield from self._ReadDirectory(location)
