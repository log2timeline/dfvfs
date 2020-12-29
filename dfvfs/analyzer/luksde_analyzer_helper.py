# -*- coding: utf-8 -*-
"""The LUKSDE format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class LUKSDEAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """LUKSDE analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_VOLUME_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_LUKSDE

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # LUKSDE signature.
    format_specification.AddNewSignature(b'LUKS\xba\xbe', offset=0)

    return format_specification


analyzer.Analyzer.RegisterHelper(LUKSDEAnalyzerHelper())
