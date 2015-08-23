# -*- coding: utf-8 -*-
"""The NTFS format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class NTFSAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Class that implements the NTFS analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_FILE_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_NTFS

  def GetFormatSpecification(self):
    """Retrieves the format specification."""
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    # NTFS file system signature.
    format_specification.AddNewSignature(b'NTFS    ', offset=3)

    return format_specification

  def IsEnabled(self):
    """Determines if the analyzer helper is enabled.

    Returns:
      A boolean value to indicate the analyzer helper is enabled.
    """
    return definitions.PREFERRED_NTFS_BACK_END == self.TYPE_INDICATOR


# Register the analyzer helpers with the analyzer.
analyzer.Analyzer.RegisterHelper(NTFSAnalyzerHelper())
