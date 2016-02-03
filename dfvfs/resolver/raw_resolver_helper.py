# -*- coding: utf-8 -*-
"""The RAW image path specification resolver helper implementation."""

# This is necessary to prevent a circular import.
import dfvfs.file_io.raw_file_io

from dfvfs.lib import definitions
from dfvfs.resolver import resolver
from dfvfs.resolver import resolver_helper


class RawResolverHelper(resolver_helper.ResolverHelper):
  """Class that implements the RAW storage media image resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_RAW

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file-like object (instance of file_io.FileIO).
    """
    return dfvfs.file_io.raw_file_io.RawFile(resolver_context)


resolver.Resolver.RegisterHelper(RawResolverHelper())
