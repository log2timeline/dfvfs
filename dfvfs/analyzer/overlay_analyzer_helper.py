# -*- coding: utf-8 -*-
"""The Overlay format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.lib import definitions


class OverlayAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Overlay analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_FILE_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_OVERLAY


analyzer.Analyzer.RegisterHelper(OverlayAnalyzerHelper())
