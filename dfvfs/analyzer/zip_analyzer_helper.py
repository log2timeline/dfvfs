# -*- coding: utf-8 -*-
"""The ZIP format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class ZipAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Class that implements the ZIP analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_ARCHIVE])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ZIP

  def GetFormatSpecification(self):
    """Retrieves the format specification."""
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # ZIP file signature.
    format_specification.AddNewSignature(b'PK\x03\x04', offset=0)

    return format_specification


# Register the analyzer helpers with the analyzer.
analyzer.Analyzer.RegisterHelper(ZipAnalyzerHelper())
