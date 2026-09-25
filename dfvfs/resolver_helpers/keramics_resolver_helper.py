# -*- coding: utf-8 -*-
"""The Keramics path specification resolver helper implementation."""

from dfvfs.file_io import keramics_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import keramics_file_system


class KeramicsResolverHelper(resolver_helper.ResolverHelper):
    """Keramics resolver helper."""

    TYPE_INDICATOR = definitions.TYPE_INDICATOR_KERAMICS

    def NewFileObject(self, resolver_context, path_spec):
        """Creates a new file input/output (IO) object.

        Args:
          resolver_context (Context): resolver context.
          path_spec (PathSpec): a path specification.

        Returns:
          FileIO: file input/output (IO) object.
        """
        return keramics_file_io.KeramicsFile(resolver_context, path_spec)

    def NewFileSystem(self, resolver_context, path_spec):
        """Creates a new file system object.

        Args:
          resolver_context (Context): resolver context.
          path_spec (PathSpec): a path specification.

        Returns:
          FileSystem: file system.
        """
        return keramics_file_system.KeramicsFileSystem(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(KeramicsResolverHelper())
