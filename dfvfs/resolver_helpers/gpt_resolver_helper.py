# -*- coding: utf-8 -*-
"""The GPT path specification resolver helper implementation."""

from dfvfs.file_io import gpt_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import gpt_file_system


class GPTResolverHelper(resolver_helper.ResolverHelper):
  """GUID Partition Table (GPT) resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_GPT

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return gpt_file_io.GPTFile(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.
    """
    return gpt_file_system.GPTFileSystem(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(GPTResolverHelper())
