# -*- coding: utf-8 -*-
"""The QCOW format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class QCOWAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Class that implements the QCOW analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_STORAGE_MEDIA_IMAGE])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_QCOW

  def GetFormatSpecification(self):
    """Retrieves the format specification."""
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # QCOW version 1 signature and version.
    format_specification.AddNewSignature(b'QFI\xfb\x00\x00\x00\x01', offset=0)

    # QCOW version 2 signature and version.
    format_specification.AddNewSignature(b'QFI\xfb\x00\x00\x00\x02', offset=0)

    # QCOW version 3 signature and version.
    format_specification.AddNewSignature(b'QFI\xfb\x00\x00\x00\x03', offset=0)

    return format_specification


# Register the analyzer helpers with the analyzer.
analyzer.Analyzer.RegisterHelper(QCOWAnalyzerHelper())
