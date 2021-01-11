# -*- coding: utf-8 -*-
"""The encrypted stream path specification resolver helper implementation."""

from dfvfs.file_io import encrypted_stream_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import encrypted_stream_file_system


class EncryptedStreamResolverHelper(resolver_helper.ResolverHelper):
  """Encrypted stream resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ENCRYPTED_STREAM

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return encrypted_stream_io.EncryptedStream(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.
    """
    return encrypted_stream_file_system.EncryptedStreamFileSystem(
        resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(EncryptedStreamResolverHelper())
