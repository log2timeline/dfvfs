# -*- coding: utf-8 -*-
"""The EXT format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class EXTAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """EXT analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_FILE_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_EXT

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # EXT file system signature.
    format_specification.AddNewSignature(b'\x53\xef', offset=1080)

    return format_specification

  def IsEnabled(self):
    """Determines if the analyzer helper is enabled.

    Returns:
      bool: True if the analyzer helper is enabled.
    """
    return definitions.PREFERRED_EXT_BACK_END == self.TYPE_INDICATOR


analyzer.Analyzer.RegisterHelper(EXTAnalyzerHelper())
