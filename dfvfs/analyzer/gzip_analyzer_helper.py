# -*- coding: utf-8 -*-
"""The GZIP format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class GzipAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """GZIP analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_COMPRESSED_STREAM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_GZIP

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # GZIP file signature.
    format_specification.AddNewSignature(b'\x1f\x8b', offset=0)

    return format_specification


analyzer.Analyzer.RegisterHelper(GzipAnalyzerHelper())
