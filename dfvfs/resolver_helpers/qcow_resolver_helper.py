# -*- coding: utf-8 -*-
"""The QCOW image path specification resolver helper implementation."""

from dfvfs.file_io import qcow_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper


class QCOWResolverHelper(resolver_helper.ResolverHelper):
  """QCOW image resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_QCOW

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return qcow_file_io.QCOWFile(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(QCOWResolverHelper())
