# -*- coding: utf-8 -*-
"""The GZIP format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class GzipAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Class that implements the GZIP analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_COMPRESSED_STREAM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_GZIP

  def GetFormatSpecification(self):
    """Retrieves the format specification."""
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # GZIP file signature.
    format_specification.AddNewSignature(b'\x1f\x8b', offset=0)

    return format_specification


# Register the analyzer helpers with the analyzer.
analyzer.Analyzer.RegisterHelper(GzipAnalyzerHelper())
