# -*- coding: utf-8 -*-
"""The XFS format analyzer helper implementation."""

from __future__ import unicode_literals

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class XFSAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """XFS analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_FILE_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_XFS

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # XFS file system signature.
    format_specification.AddNewSignature(b'XFSB', offset=0)

    return format_specification


analyzer.Analyzer.RegisterHelper(XFSAnalyzerHelper())
