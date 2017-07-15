# -*- coding: utf-8 -*-
"""The encrypted stream path specification resolver helper implementation."""

from __future__ import unicode_literals

# This is necessary to prevent a circular import.
import dfvfs.file_io.encrypted_stream_io
import dfvfs.vfs.encrypted_stream_file_system

from dfvfs.lib import definitions
from dfvfs.resolver import resolver
from dfvfs.resolver import resolver_helper


class EncryptedStreamResolverHelper(resolver_helper.ResolverHelper):
  """Encrypted stream resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ENCRYPTED_STREAM

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return dfvfs.file_io.encrypted_stream_io.EncryptedStream(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return dfvfs.vfs.encrypted_stream_file_system.EncryptedStreamFileSystem(
        resolver_context)


resolver.Resolver.RegisterHelper(EncryptedStreamResolverHelper())
