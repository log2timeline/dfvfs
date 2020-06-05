# -*- coding: utf-8 -*-
"""The XZ format analyzer helper implementation."""

from __future__ import unicode_literals

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class XZAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """XZ analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_COMPRESSED_STREAM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_XZ

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # XZ compressed steam signature.
    format_specification.AddNewSignature(b'\xfd7zXZ\x00', offset=0)

    return format_specification


analyzer.Analyzer.RegisterHelper(XZAnalyzerHelper())
