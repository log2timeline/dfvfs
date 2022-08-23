# -*- coding: utf-8 -*-
"""The FAT format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class FATAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """FAT analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_FILE_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FAT

  def GetFormatSpecification(self):
    """Retrieves the format specification.

    Returns:
      FormatSpecification: format specification or None if the format cannot
          be defined by a specification object.
    """
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # Boot sector signature.
    format_specification.AddNewSignature(b'\x55\xaa', offset=510)

    # FAT-12 and FAT-16 file system hint.
    format_specification.AddNewSignature(b'FAT12   ', offset=54)
    format_specification.AddNewSignature(b'FAT16   ', offset=54)

    # FAT-32 file system hint.
    format_specification.AddNewSignature(b'FAT32   ', offset=82)

    # exFAT file system signature.
    format_specification.AddNewSignature(b'EXFAT   ', offset=3)

    return format_specification

  def IsEnabled(self):
    """Determines if the analyzer helper is enabled.

    Returns:
      bool: True if the analyzer helper is enabled.
    """
    return definitions.PREFERRED_FAT_BACK_END == self.TYPE_INDICATOR


analyzer.Analyzer.RegisterHelper(FATAnalyzerHelper())
