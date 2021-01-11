# -*- coding: utf-8 -*-
"""The compressed stream path specification resolver helper implementation."""

from dfvfs.file_io import compressed_stream_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import compressed_stream_file_system


class CompressedStreamResolverHelper(resolver_helper.ResolverHelper):
  """Compressed stream resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_COMPRESSED_STREAM

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return compressed_stream_io.CompressedStream(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.
    """
    return compressed_stream_file_system.CompressedStreamFileSystem(
        resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(CompressedStreamResolverHelper())
