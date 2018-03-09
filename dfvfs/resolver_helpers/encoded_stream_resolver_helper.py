# -*- coding: utf-8 -*-
"""The encoded stream path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import encoded_stream_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import encoded_stream_file_system


class EncodedStreamResolverHelper(resolver_helper.ResolverHelper):
  """Encoded stream resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ENCODED_STREAM

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return encoded_stream_io.EncodedStream(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return encoded_stream_file_system.EncodedStreamFileSystem(resolver_context)


manager.ResolverHelperManager.RegisterHelper(EncodedStreamResolverHelper())
