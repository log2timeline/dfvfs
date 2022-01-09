# -*- coding: utf-8 -*-
"""The PHDI format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class PHDIAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """PHDI analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_STORAGE_MEDIA_IMAGE])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_PHDI

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # PHDI descriptor file signature.
    format_specification.AddNewSignature(
        b'<Parallels_disk_image ', offset=0x27)

    return format_specification


analyzer.Analyzer.RegisterHelper(PHDIAnalyzerHelper())
