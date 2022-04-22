# -*- coding: utf-8 -*-
"""The Overlay directory implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory
from dfvfs.resolver import context
from dfvfs.resolver import resolver
from dfvfs.vfs import directory
from dfvfs.vfs import ext_file_system
from dfvfs.vfs import ext_directory

class OverlayDirectory(directory.Directory):
  """Overlay directory."""

  def __init__(self, file_system, path_spec):
    """Initializes an Overlay directory.

    Args:
      file_system (OverlayFileSystem): file system.
      path_spec (OverlayPathSpec): path specification.
    """
    pass

  def _ReadDirectory(self, location):
    """Enumerates the upper and lower layers of the Overlay filesystem.

    Args:
      location (str): the location in the Overlay.

    Yields:
      OverlayPathSpec: Overlay Path Specification.
    """
    visited_paths = set([location])
    whiteouts = set()

    resolver_context = context.Context()

    layer_specs = [self._file_system.upper_path_spec]
    layer_specs.extend(self._file_system.lower_path_specs)

    for layer in layer_specs:
      if location in whiteouts:
        continue

      layer_filesystem = ext_file_system.EXTFileSystem(resolver_context, layer)
      layer_filesystem.Open()

      layer_path_spec = factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_EXT, location=layer.location + location,
          parent=layer.parent)

      if not layer_filesystem.FileEntryExistsByPathSpec(layer_path_spec):
        continue

      layer_file_entry = resolver.Resolver.OpenFileEntry(layer_path_spec)
      for attribute in layer_file_entry.attributes:
        if (attribute.name == 'trusted.overlay.opaque' and
            attribute.read() == b'y'):
          whiteouts.add(location)

      layer_directory = ext_directory.EXTDirectory(
          layer_filesystem, layer_path_spec,
          layer_file_entry.GetEXTFileEntry())
      if not layer_directory:
        continue

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
