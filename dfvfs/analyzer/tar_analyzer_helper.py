# -*- coding: utf-8 -*-
"""The TAR format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class TARAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Class that implements the TAR analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_ARCHIVE])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TAR

  def GetFormatSpecification(self):
    """Retrieves the format specification."""
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # TAR file signature.
    format_specification.AddNewSignature(b'ustar\x00', offset=257)

    # Old TAR file signature.
    format_specification.AddNewSignature(b'ustar\x20\x20\x00', offset=257)

    return format_specification


# Register the analyzer helpers with the analyzer.
analyzer.Analyzer.RegisterHelper(TARAnalyzerHelper())
