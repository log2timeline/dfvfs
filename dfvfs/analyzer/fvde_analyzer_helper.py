# -*- coding: utf-8 -*-
"""The FVDE format analyzer helper implementation."""

from __future__ import unicode_literals

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class FVDEAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """FVDE analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_VOLUME_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FVDE

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # FVDE CoreStorage signature.
    format_specification.AddNewSignature(b'CS', offset=88)

    return format_specification


analyzer.Analyzer.RegisterHelper(FVDEAnalyzerHelper())
