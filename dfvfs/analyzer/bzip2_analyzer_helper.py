# -*- coding: utf-8 -*-
"""The BZIP2 format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class BZIP2AnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """BZIP2 analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_COMPRESSED_STREAM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BZIP2

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # TODO: add support for signature chains so that we add the 'BZ' at
    # offset 0.

    # BZIP2 compressed steam signature.
    format_specification.AddNewSignature(b'\x31\x41\x59\x26\x53\x59', offset=4)

    return format_specification


analyzer.Analyzer.RegisterHelper(BZIP2AnalyzerHelper())
