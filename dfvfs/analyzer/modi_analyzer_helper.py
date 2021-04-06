# -*- coding: utf-8 -*-
"""The Mac OS disk image (MODI) format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class MODIAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Mac OS disk image (MODI) analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_STORAGE_MEDIA_IMAGE])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_MODI

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # Sparse disk image (.sparseimage) signature in header.
    format_specification.AddNewSignature(b'sprs', offset=0)

    # Universal Disk Image Format (UDIF) (.dmg) signature in footer.
    format_specification.AddNewSignature(b'koly', offset=-512)

    return format_specification


analyzer.Analyzer.RegisterHelper(MODIAnalyzerHelper())
