# -*- coding: utf-8 -*-
"""The CPIO format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class CPIOAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """CPIO analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_ARCHIVE])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_CPIO

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # CPIO binary file big-endian signature.
    format_specification.AddNewSignature(b'\x71\xc7', offset=0)

    # CPIO binary file little-endian signature.
    format_specification.AddNewSignature(b'\xc7\x71', offset=0)

    # CPIO portable ASCII file signature.
    format_specification.AddNewSignature(b'070707', offset=0)

    # CPIO new ASCII file signature.
    format_specification.AddNewSignature(b'070701', offset=0)

    # CPIO new ASCII file with checksum signature.
    format_specification.AddNewSignature(b'070702', offset=0)

    return format_specification


analyzer.Analyzer.RegisterHelper(CPIOAnalyzerHelper())
