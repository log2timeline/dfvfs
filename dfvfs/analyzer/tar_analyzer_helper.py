# -*- coding: utf-8 -*-
"""The TAR format analyzer helper implementation."""

from __future__ import unicode_literals

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class TARAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """TAR analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_ARCHIVE])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TAR

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # TAR file signature.
    format_specification.AddNewSignature(b'ustar\x00', offset=257)

    # Old TAR file signature.
    format_specification.AddNewSignature(b'ustar\x20\x20\x00', offset=257)

    return format_specification


analyzer.Analyzer.RegisterHelper(TARAnalyzerHelper())
