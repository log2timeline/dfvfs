# -*- coding: utf-8 -*-
"""The data range path specification resolver helper implementation."""

# This is necessary to prevent a circular import.
import dfvfs.file_io.data_range_io

from dfvfs.lib import definitions
from dfvfs.resolver import resolver
from dfvfs.resolver import resolver_helper


class DataRangeResolverHelper(resolver_helper.ResolverHelper):
  """Class that implements the data range resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_DATA_RANGE

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file-like object (instance of file_io.FileIO).
    """
    return dfvfs.file_io.data_range_io.DataRange(resolver_context)


resolver.Resolver.RegisterHelper(DataRangeResolverHelper())
