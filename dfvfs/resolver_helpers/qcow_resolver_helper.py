# -*- coding: utf-8 -*-
"""The QCOW image path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import qcow_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper


class QCOWResolverHelper(resolver_helper.ResolverHelper):
  """QCOW image resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_QCOW

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return qcow_file_io.QCOWFile(resolver_context)


manager.ResolverHelperManager.RegisterHelper(QCOWResolverHelper())
