# -*- coding: utf-8 -*-
"""The VHDI format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class VHDIAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Class that implements the VHDI analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_STORAGE_MEDIA_IMAGE])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VHDI

  def GetFormatSpecification(self):
    """Retrieves the format specification."""
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # VHDI image signature in footer.
    format_specification.AddNewSignature(b'conectix', offset=-512)

    # VHDI image signature in copy of footer in differential
    # or dynamic disk image.
    format_specification.AddNewSignature(b'conectix', offset=0)

    return format_specification


# Register the analyzer helpers with the analyzer.
analyzer.Analyzer.RegisterHelper(VHDIAnalyzerHelper())
