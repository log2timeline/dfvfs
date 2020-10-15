# -*- coding: utf-8 -*-
"""The HFS format analyzer helper implementation."""

from __future__ import unicode_literals

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class HFSAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """HFS analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_FILE_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_HFS

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # HFS+ file system signature.
    format_specification.AddNewSignature(b'H+', offset=1024)

    # HFSX file system signature.
    format_specification.AddNewSignature(b'HX', offset=1024)

    return format_specification

  def IsEnabled(self):
    """Determines if the analyzer helper is enabled.

    Returns:
      bool: True if the analyzer helper is enabled.
    """
    return definitions.PREFERRED_HFS_BACK_END == self.TYPE_INDICATOR


analyzer.Analyzer.RegisterHelper(HFSAnalyzerHelper())
