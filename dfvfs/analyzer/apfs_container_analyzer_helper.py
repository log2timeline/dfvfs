# -*- coding: utf-8 -*-
"""The APFS container format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class APFSContainerAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """APFS container analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_VOLUME_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_APFS_CONTAINER

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # APFS container signature.
    format_specification.AddNewSignature(b'NXSB', offset=32)

    return format_specification


analyzer.Analyzer.RegisterHelper(APFSContainerAnalyzerHelper())
